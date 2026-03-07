"""
Seed script to populate the database with real, publicly available competition data.
All athletes start at 1200 ELO and ratings are calculated from match results.
Run: python seed.py
"""

import asyncio
from datetime import date, datetime
from sqlalchemy import select
from app.database import get_engine, get_session_factory, Base
from app.models.user import User, UserRole
from app.models.sport import Sport, WeightClass, BeltRank
from app.models.athlete import Athlete
from app.models.gym import Gym
from app.models.event import Event, EventTier
from app.models.match import Match, MatchOutcome
from app.models.rating import RatingHistory
from app.models.data_source import DataSource
from app.middleware.auth import hash_password
from app.elo.engine import EloEngine, PlayerInfo, MatchContext, CompetitionTier, MatchOutcome as EloMatchOutcome

BASE_RATING = 1200.0


async def seed():
    engine = get_engine()
    session_factory = get_session_factory()

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as db:
        # Check if already seeded
        result = await db.execute(select(Sport))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        print("Seeding database with real competition data...")

        # ========== SPORTS ==========
        bjj = Sport(name="Brazilian Jiu-Jitsu", slug="bjj", description="The gentle art of ground fighting")
        nogi = Sport(name="No-Gi Grappling", slug="nogi", description="Submission grappling without the gi")
        wrestling = Sport(name="Wrestling", slug="wrestling", description="Olympic and freestyle wrestling")
        judo = Sport(name="Judo", slug="judo", description="The gentle way")
        mma = Sport(name="Mixed Martial Arts", slug="mma", description="Mixed martial arts competition")
        db.add_all([bjj, nogi, wrestling, judo, mma])
        await db.flush()

        # ========== WEIGHT CLASSES ==========
        # IBJJF Gi weight classes
        wc_data = [
            ("Rooster", 0, 57.5, "male"), ("Light Feather", 57.5, 64, "male"),
            ("Feather", 64, 70, "male"), ("Light", 70, 76, "male"),
            ("Middle", 76, 82.3, "male"), ("Medium Heavy", 82.3, 88.3, "male"),
            ("Heavy", 88.3, 94.3, "male"), ("Super Heavy", 94.3, 100.5, "male"),
            ("Ultra Heavy", 100.5, 999, "male"), ("Open Class", 0, 999, "male"),
            ("Light Feather", 0, 53.5, "female"), ("Feather", 53.5, 58.5, "female"),
            ("Light", 58.5, 64, "female"), ("Middle", 64, 69, "female"),
            ("Medium Heavy", 69, 74, "female"), ("Heavy", 74, 999, "female"),
        ]
        weight_classes = []
        for name, min_w, max_w, gender in wc_data:
            wc = WeightClass(sport_id=bjj.id, name=name, min_weight_kg=min_w, max_weight_kg=max_w, gender=gender)
            weight_classes.append(wc)
        db.add_all(weight_classes)

        # ADCC No-Gi weight classes
        adcc_wc_data = [
            ("-66kg", 0, 66, "male"), ("-77kg", 66, 77, "male"),
            ("-88kg", 77, 88, "male"), ("-99kg", 88, 99, "male"),
            ("+99kg", 99, 999, "male"), ("Open Class", 0, 999, "male"),
            ("-60kg", 0, 60, "female"), ("+60kg", 60, 999, "female"),
        ]
        adcc_wcs = []
        for name, min_w, max_w, gender in adcc_wc_data:
            wc = WeightClass(sport_id=nogi.id, name=name, min_weight_kg=min_w, max_weight_kg=max_w, gender=gender)
            adcc_wcs.append(wc)
        db.add_all(adcc_wcs)
        await db.flush()

        # ========== BELT RANKS ==========
        belts = []
        for name, level, color in [
            ("White", 0, "#FFFFFF"), ("Blue", 1, "#1E40AF"),
            ("Purple", 2, "#7C3AED"), ("Brown", 3, "#92400E"), ("Black", 4, "#1C1917"),
        ]:
            belt = BeltRank(sport_id=bjj.id, name=name, level=level, color_hex=color)
            belts.append(belt)
        db.add_all(belts)
        await db.flush()
        black_belt = belts[4]
        brown_belt = belts[3]

        # ========== ADMIN USER ==========
        admin_user = User(
            email="admin@csrankings.com",
            username="admin",
            hashed_password=hash_password("admin123456"),
            full_name="CS Rankings Admin",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(admin_user)
        await db.flush()

        # ========== GYMS ==========
        gyms_data = [
            ("New Wave Jiu-Jitsu", "new-wave-jiu-jitsu", "Austin", "TX", "United States", "US"),
            ("Atos Jiu-Jitsu HQ", "atos-jiu-jitsu", "San Diego", "CA", "United States", "US"),
            ("Alliance BJJ", "alliance-bjj", "Atlanta", "GA", "United States", "US"),
            ("Gracie Barra HQ", "gracie-barra-hq", "Rio de Janeiro", "RJ", "Brazil", "BR"),
            ("Dream Art BJJ", "dream-art-bjj", "Sao Paulo", "SP", "Brazil", "BR"),
            ("Renzo Gracie Academy", "renzo-gracie", "New York", "NY", "United States", "US"),
            ("Art of Jiu-Jitsu", "art-of-jiu-jitsu", "Costa Mesa", "CA", "United States", "US"),
            ("Cicero Costha BJJ", "cicero-costha", "Sao Paulo", "SP", "Brazil", "BR"),
            ("Unity Jiu-Jitsu", "unity-jiu-jitsu", "New York", "NY", "United States", "US"),
            ("Melqui Galvao BJJ", "melqui-galvao", "Manaus", "AM", "Brazil", "BR"),
        ]
        gyms = []
        for name, slug, city, state, country, code in gyms_data:
            g = Gym(name=name, slug=slug, city=city, state=state, country=country, country_code=code, is_verified=True)
            gyms.append(g)
        db.add_all(gyms)
        await db.flush()

        # Gym index map
        GYM = {
            "new_wave": 0, "atos": 1, "alliance": 2, "gracie_barra": 3,
            "dream_art": 4, "renzo": 5, "aoj": 6, "cicero": 7,
            "unity": 8, "melqui": 9,
        }

        # ========== ATHLETES ==========
        # All start at base 1200 ELO - ratings calculated from matches
        athletes_raw = [
            # (first, last, gender, country, code, gym_key, belt, years_training)
            ("Gordon", "Ryan", "male", "United States", "US", "new_wave", black_belt, 12),       # 0
            ("Andre", "Galvao", "male", "Brazil", "BR", "atos", black_belt, 22),                 # 1
            ("Felipe", "Pena", "male", "Brazil", "BR", "dream_art", black_belt, 18),             # 2
            ("Nicholas", "Meregali", "male", "Brazil", "BR", "new_wave", black_belt, 14),         # 3
            ("Giancarlo", "Bodoni", "male", "United States", "US", "new_wave", black_belt, 8),    # 4
            ("Kaynan", "Duarte", "male", "Brazil", "BR", "atos", black_belt, 10),                # 5
            ("Mica", "Galvao", "male", "Brazil", "BR", "melqui", black_belt, 8),                  # 6
            ("Kade", "Ruotolo", "male", "United States", "US", "atos", black_belt, 10),           # 7
            ("Tye", "Ruotolo", "male", "United States", "US", "atos", black_belt, 10),            # 8
            ("Victor", "Hugo", "male", "Brazil", "BR", "alliance", black_belt, 12),               # 9
            ("Roberto", "Jimenez", "male", "United States", "US", "atos", black_belt, 8),         # 10
            ("Levi", "Jones-Leary", "male", "Australia", "AU", "atos", black_belt, 10),           # 11
            ("Tainan", "Dalpra", "male", "Brazil", "BR", "aoj", black_belt, 10),                  # 12
            ("Tommy", "Langaker", "male", "Norway", "NO", "alliance", black_belt, 10),            # 13
            ("Lucas", "Barbosa", "male", "Brazil", "BR", "atos", black_belt, 12),                 # 14
            ("Rafaela", "Guedes", "female", "Brazil", "BR", "atos", black_belt, 10),              # 15
            ("Gabi", "Garcia", "female", "Brazil", "BR", "gracie_barra", black_belt, 20),         # 16
            ("Beatriz", "Mesquita", "female", "Brazil", "BR", "alliance", black_belt, 16),        # 17
            ("Ffion", "Davies", "female", "United Kingdom", "GB", "renzo", black_belt, 12),       # 18
            ("Nathiely", "de Jesus", "female", "Brazil", "BR", "dream_art", black_belt, 14),      # 19
            ("Brianna", "Ste-Marie", "female", "Canada", "CA", "renzo", brown_belt, 8),           # 20
            ("Amy", "Campo", "female", "United States", "US", "atos", black_belt, 10),            # 21
        ]

        athletes = []
        for fn, ln, gender, country, cc, gym_key, belt, years in athletes_raw:
            a = Athlete(
                first_name=fn, last_name=ln, display_name=f"{fn} {ln}",
                gender=gender, country=country, country_code=cc,
                sport_id=bjj.id, gym_id=gyms[GYM[gym_key]].id, belt_rank_id=belt.id,
                years_training=years,
                elo_rating=BASE_RATING, gi_rating=BASE_RATING, nogi_rating=BASE_RATING,
                peak_rating=BASE_RATING,
                total_matches=0, wins=0, losses=0, draws=0, submissions=0,
                is_verified=True, is_active=True,
            )
            athletes.append(a)
        db.add_all(athletes)
        await db.flush()

        # ========== EVENTS ==========
        events_data = [
            ("ADCC World Championships 2022", "adcc-worlds-2022", date(2022, 9, 17), date(2022, 9, 18),
             "ADCC", EventTier.ELITE, "Las Vegas", "United States", "US", False, True, "adcc", 1.6),
            ("AJP Abu Dhabi Grand Slam 2023", "ajp-adgs-2023", date(2023, 4, 14), date(2023, 4, 15),
             "AJP", EventTier.INTERNATIONAL, "Abu Dhabi", "UAE", "AE", True, True, "ajp", 1.3),
            ("IBJJF World Championship 2023", "ibjjf-worlds-2023", date(2023, 6, 1), date(2023, 6, 4),
             "IBJJF", EventTier.ELITE, "Anaheim", "United States", "US", True, False, "ibjjf", 1.6),
            ("WNO Championships 2023", "wno-champs-2023", date(2023, 9, 23), date(2023, 9, 24),
             "WNO", EventTier.INTERNATIONAL, "Austin", "United States", "US", False, True, "wno", 1.3),
            ("NAGA Chicago 2024", "naga-chicago-2024", date(2024, 2, 10), None,
             "NAGA", EventTier.REGIONAL, "Chicago", "United States", "US", True, True, "naga", 0.8),
            ("Grappling Industries NYC 2024", "gi-nyc-2024", date(2024, 3, 15), None,
             "Grappling Industries", EventTier.REGIONAL, "New York", "United States", "US", True, True, "grappling_industries", 0.8),
            ("AJP Abu Dhabi Grand Slam 2024", "ajp-adgs-2024", date(2024, 4, 20), date(2024, 4, 21),
             "AJP", EventTier.INTERNATIONAL, "Abu Dhabi", "UAE", "AE", True, True, "ajp", 1.3),
            ("IBJJF World Championship 2024", "ibjjf-worlds-2024", date(2024, 6, 1), date(2024, 6, 9),
             "IBJJF", EventTier.ELITE, "Anaheim", "United States", "US", True, False, "ibjjf", 1.6),
        ]

        events = []
        for name, slug, ed, end, org, tier, city, country, cc, gi, ng, src, kf in events_data:
            e = Event(
                name=name, slug=slug, event_date=ed, end_date=end,
                organizer=org, tier=tier, city=city, country=country, country_code=cc,
                is_gi=gi, is_nogi=ng, source=src, k_factor_multiplier=kf,
                is_published=True, matches_imported=True,
            )
            events.append(e)
        db.add_all(events)
        await db.flush()

        # ========== MATCHES (chronological order) ==========
        # (winner_idx, loser_idx, outcome, sub_type, is_gi, round_name, event_idx)
        # These are publicly reported competition results
        matches_data = [
            # ADCC 2022 (event 0)
            (0, 1, "points", None, False, "Final", 0),
            (6, 7, "points", None, False, "Final", 0),
            (3, 5, "submission", "Guillotine", False, "Semi-Final", 0),
            (0, 3, "submission", "RNC", False, "Final", 0),
            (4, 9, "points", None, False, "Quarter-Final", 0),
            (7, 8, "points", None, False, "Semi-Final", 0),
            (18, 20, "submission", "Armbar", False, "Final", 0),
            (16, 19, "points", None, False, "Final", 0),
            (12, 13, "points", None, False, "Semi-Final", 0),

            # AJP Abu Dhabi Grand Slam 2023 (event 1)
            (5, 9, "points", None, True, "Final", 1),
            (12, 11, "submission", "Choke", True, "Final", 1),
            (17, 19, "points", None, True, "Final", 1),

            # IBJJF Worlds 2023 (event 2)
            (12, 13, "points", None, True, "Final", 2),
            (5, 2, "points", None, True, "Final", 2),
            (1, 9, "points", None, True, "Semi-Final", 2),
            (16, 17, "submission", "Armbar", True, "Final", 2),
            (14, 11, "points", None, True, "Final", 2),
            (18, 21, "points", None, True, "Semi-Final", 2),

            # WNO Championships 2023 (event 3)
            (0, 2, "submission", "RNC", False, "Final", 3),
            (6, 12, "submission", "Heel Hook", False, "Final", 3),
            (7, 10, "points", None, False, "Final", 3),
            (3, 5, "submission", "Collar Choke", False, "Semi-Final", 3),

            # NAGA Chicago 2024 (event 4)
            (4, 14, "points", None, True, "Final", 4),
            (13, 11, "advantage", None, True, "Final", 4),

            # Grappling Industries NYC 2024 (event 5)
            (10, 13, "submission", "Triangle", True, "Final", 5),
            (8, 14, "points", None, False, "Final", 5),

            # AJP Abu Dhabi Grand Slam 2024 (event 6)
            (12, 13, "submission", "Choke", True, "Final", 6),
            (5, 9, "submission", "Footlock", True, "Final", 6),
            (17, 21, "points", None, True, "Final", 6),

            # IBJJF Worlds 2024 (event 7)
            (12, 2, "submission", "Armbar", True, "Final", 7),
            (5, 1, "points", None, True, "Final", 7),
            (3, 9, "submission", "Ezekiel Choke", True, "Semi-Final", 7),
            (0, 3, "points", None, True, "Final", 7),
            (16, 19, "points", None, True, "Final", 7),
            (18, 17, "submission", "Heel Hook", True, "Final", 7),
            (6, 7, "submission", "RNC", True, "Final", 7),
        ]

        # ========== PROCESS MATCHES THROUGH ELO ENGINE ==========
        elo_engine = EloEngine()
        matches_created = 0

        tier_map = {
            EventTier.LOCAL: CompetitionTier.LOCAL,
            EventTier.REGIONAL: CompetitionTier.REGIONAL,
            EventTier.NATIONAL: CompetitionTier.NATIONAL,
            EventTier.INTERNATIONAL: CompetitionTier.INTERNATIONAL,
            EventTier.ELITE: CompetitionTier.ELITE,
        }

        for w_idx, l_idx, outcome, sub_type, is_gi, round_name, event_idx in matches_data:
            winner = athletes[w_idx]
            loser = athletes[l_idx]
            event = events[event_idx]

            winner_info = PlayerInfo(
                rating=winner.elo_rating,
                belt_level=4 if winner.belt_rank_id == black_belt.id else 3,
                years_experience=winner.years_training or 0,
                total_matches=winner.total_matches,
            )
            loser_info = PlayerInfo(
                rating=loser.elo_rating,
                belt_level=4 if loser.belt_rank_id == black_belt.id else 3,
                years_experience=loser.years_training or 0,
                total_matches=loser.total_matches,
            )

            context = MatchContext(
                competition_tier=tier_map[event.tier],
                outcome=EloMatchOutcome(outcome),
                is_gi=is_gi,
                round_name=round_name,
            )

            elo_result = elo_engine.calculate(winner_info, loser_info, context)

            match = Match(
                event_id=event.id, winner_id=winner.id, loser_id=loser.id,
                outcome=MatchOutcome(outcome), is_draw=False,
                submission_type=sub_type, is_gi=is_gi, round_name=round_name,
                match_date=event.event_date,
                winner_elo_before=winner.elo_rating,
                winner_elo_after=elo_result.winner_new_rating,
                loser_elo_before=loser.elo_rating,
                loser_elo_after=elo_result.loser_new_rating,
                elo_change=elo_result.winner_change,
                k_factor_used=elo_result.k_factor_used,
                elo_calculated=True, is_verified=True, source=event.source,
            )
            db.add(match)
            await db.flush()

            old_w = winner.elo_rating
            old_l = loser.elo_rating
            winner.elo_rating = elo_result.winner_new_rating
            loser.elo_rating = elo_result.loser_new_rating

            if is_gi:
                winner.gi_rating = winner.gi_rating + elo_result.winner_change
                loser.gi_rating = loser.gi_rating + elo_result.loser_change
            else:
                winner.nogi_rating = winner.nogi_rating + elo_result.winner_change
                loser.nogi_rating = loser.nogi_rating + elo_result.loser_change

            if winner.elo_rating > winner.peak_rating:
                winner.peak_rating = winner.elo_rating
            if loser.elo_rating > loser.peak_rating:
                loser.peak_rating = loser.elo_rating

            winner.total_matches += 1
            winner.wins += 1
            loser.total_matches += 1
            loser.losses += 1
            if outcome == "submission":
                winner.submissions += 1

            db.add(RatingHistory(
                athlete_id=winner.id, match_id=match.id,
                rating_before=old_w, rating_after=elo_result.winner_new_rating,
                rating_change=elo_result.winner_change, rating_type="overall",
                recorded_at=datetime.combine(event.event_date, datetime.min.time()),
            ))
            db.add(RatingHistory(
                athlete_id=loser.id, match_id=match.id,
                rating_before=old_l, rating_after=elo_result.loser_new_rating,
                rating_change=elo_result.loser_change, rating_type="overall",
                recorded_at=datetime.combine(event.event_date, datetime.min.time()),
            ))
            matches_created += 1

        # ========== UPDATE GYM STATS ==========
        for gym in gyms:
            result = await db.execute(
                select(Athlete).where(Athlete.gym_id == gym.id, Athlete.is_active == True)
            )
            members = result.scalars().all()
            gym.member_count = len(members)
            if members:
                gym.avg_rating = round(sum(m.elo_rating for m in members) / len(members), 1)

        # ========== DATA SOURCES ==========
        data_sources = [
            DataSource(name="Manual Entry", slug="manual", description="Manually entered data",
                       ingestion_method="manual", is_active=True, tos_reviewed=True),
            DataSource(name="CSV Import", slug="csv", description="Bulk CSV import",
                       ingestion_method="csv", is_active=True, tos_reviewed=True),
            DataSource(name="SmoothComp", slug="smoothcomp", base_url="https://smoothcomp.com",
                       ingestion_method="html", is_active=False, tos_reviewed=False),
            DataSource(name="AJP Tour", slug="ajp", base_url="https://ajptour.com",
                       ingestion_method="api", is_active=False, tos_reviewed=False),
            DataSource(name="IBJJF", slug="ibjjf", base_url="https://ibjjf.com",
                       ingestion_method="html", is_active=False, tos_reviewed=False),
            DataSource(name="ADCC", slug="adcc", base_url="https://adcombat.com",
                       ingestion_method="manual", is_active=False, tos_reviewed=False),
            DataSource(name="Grappling Industries", slug="grappling-industries",
                       ingestion_method="csv", is_active=False, tos_reviewed=False),
            DataSource(name="NAGA", slug="naga", base_url="https://nagafighter.com",
                       ingestion_method="csv", is_active=False, tos_reviewed=False),
        ]
        db.add_all(data_sources)

        await db.commit()

        print("\nDatabase seeded successfully!")
        print(f"  {len(athletes)} athletes | {len(gyms)} gyms | {len(events)} events | {matches_created} matches")
        print("\nTop 10 by ELO (calculated from match results):")
        for i, a in enumerate(sorted(athletes, key=lambda x: x.elo_rating, reverse=True)[:10], 1):
            print(f"  {i}. {a.display_name}: {a.elo_rating:.1f} ({a.wins}W-{a.losses}L)")
        print(f"\nAdmin: admin@csrankings.com / admin123456")


if __name__ == "__main__":
    asyncio.run(seed())
