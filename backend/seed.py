"""
Seed script to populate the database with example data.
Run: python seed.py
"""

import asyncio
import uuid
from datetime import date, datetime
from sqlalchemy import select
from app.database import engine, async_session, Base
from app.models.user import User, UserRole
from app.models.sport import Sport, WeightClass, BeltRank
from app.models.athlete import Athlete
from app.models.gym import Gym
from app.models.event import Event, EventTier
from app.models.match import Match, MatchOutcome
from app.models.rating import RatingHistory
from app.middleware.auth import hash_password
from app.elo.engine import EloEngine, PlayerInfo, MatchContext, CompetitionTier, MatchOutcome as EloMatchOutcome


async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Check if already seeded
        result = await db.execute(select(Sport))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...")

        # --- Sports ---
        bjj = Sport(name="Brazilian Jiu-Jitsu", slug="bjj", description="The gentle art")
        wrestling = Sport(name="Wrestling", slug="wrestling", description="Olympic wrestling")
        judo = Sport(name="Judo", slug="judo", description="The gentle way")
        mma = Sport(name="Mixed Martial Arts", slug="mma", description="Mixed martial arts")
        db.add_all([bjj, wrestling, judo, mma])
        await db.flush()

        # --- Weight Classes (BJJ) ---
        weight_classes = []
        for name, min_w, max_w, gender in [
            ("Rooster", 0, 57.5, "male"), ("Light Feather", 57.5, 64, "male"),
            ("Feather", 64, 70, "male"), ("Light", 70, 76, "male"),
            ("Middle", 76, 82.3, "male"), ("Medium Heavy", 82.3, 88.3, "male"),
            ("Heavy", 88.3, 94.3, "male"), ("Super Heavy", 94.3, 100.5, "male"),
            ("Ultra Heavy", 100.5, 999, "male"), ("Open Class", 0, 999, "male"),
            ("Light Feather", 0, 53.5, "female"), ("Feather", 53.5, 58.5, "female"),
            ("Light", 58.5, 64, "female"), ("Middle", 64, 69, "female"),
            ("Medium Heavy", 69, 74, "female"), ("Heavy", 74, 999, "female"),
        ]:
            wc = WeightClass(sport_id=bjj.id, name=name, min_weight_kg=min_w, max_weight_kg=max_w, gender=gender)
            weight_classes.append(wc)
        db.add_all(weight_classes)
        await db.flush()

        # --- Belt Ranks ---
        belts = []
        for name, level, color in [
            ("White", 0, "#FFFFFF"), ("Blue", 1, "#0000FF"),
            ("Purple", 2, "#800080"), ("Brown", 3, "#8B4513"), ("Black", 4, "#000000"),
        ]:
            belt = BeltRank(sport_id=bjj.id, name=name, level=level, color_hex=color)
            belts.append(belt)
        db.add_all(belts)
        await db.flush()
        black_belt = belts[4]
        brown_belt = belts[3]
        purple_belt = belts[2]

        # --- Admin User ---
        admin = User(
            email="admin@csrankings.com",
            username="admin",
            hashed_password=hash_password("admin123456"),
            full_name="CS Rankings Admin",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(admin)
        await db.flush()

        # --- Gyms ---
        gyms_data = [
            ("New Wave Jiu-Jitsu", "new-wave-jiu-jitsu", "Austin", "TX", "United States", "US"),
            ("Atos Jiu-Jitsu HQ", "atos-jiu-jitsu", "San Diego", "CA", "United States", "US"),
            ("Alliance BJJ", "alliance-bjj", "Atlanta", "GA", "United States", "US"),
            ("Gracie Barra HQ", "gracie-barra-hq", "Rio de Janeiro", "RJ", "Brazil", "BR"),
            ("Dream Art BJJ", "dream-art-bjj", "Sao Paulo", "SP", "Brazil", "BR"),
            ("Renzo Gracie Academy", "renzo-gracie", "New York", "NY", "United States", "US"),
        ]
        gyms = []
        for name, slug, city, state, country, code in gyms_data:
            g = Gym(name=name, slug=slug, city=city, state=state, country=country, country_code=code, is_verified=True)
            gyms.append(g)
        db.add_all(gyms)
        await db.flush()

        # --- Athletes ---
        athletes_data = [
            ("Gordon", "Ryan", "male", "United States", "US", 0, black_belt.id, 12, 2145, 2020, 2270, 48, 42, 6, 0, 28),
            ("Andre", "Galvao", "male", "Brazil", "BR", 1, black_belt.id, 22, 2098, 2050, 2146, 62, 54, 8, 0, 30),
            ("Felipe", "Pena", "male", "Brazil", "BR", 4, black_belt.id, 18, 2067, 2040, 2094, 55, 47, 8, 0, 22),
            ("Nicholas", "Meregali", "male", "Brazil", "BR", 2, black_belt.id, 14, 2034, 2010, 2058, 41, 36, 5, 0, 18),
            ("Giancarlo", "Bodoni", "male", "United States", "US", 0, black_belt.id, 8, 2012, 1990, 2034, 35, 30, 5, 0, 14),
            ("Kaynan", "Duarte", "male", "Brazil", "BR", 1, black_belt.id, 10, 1998, 1980, 2016, 44, 38, 6, 0, 16),
            ("Mica", "Galvao", "male", "Brazil", "BR", 4, black_belt.id, 8, 1987, 1950, 2024, 38, 34, 4, 0, 20),
            ("Kade", "Ruotolo", "male", "United States", "US", 1, black_belt.id, 10, 1965, 1920, 2010, 32, 28, 4, 0, 16),
            ("Tye", "Ruotolo", "male", "United States", "US", 1, black_belt.id, 10, 1952, 1910, 1994, 30, 26, 4, 0, 14),
            ("Victor", "Hugo", "male", "Brazil", "BR", 2, black_belt.id, 12, 1940, 1920, 1960, 42, 35, 7, 0, 15),
            ("Gabi", "Garcia", "female", "Brazil", "BR", 3, black_belt.id, 20, 1920, 1900, 1940, 45, 40, 5, 0, 18),
            ("Beatriz", "Mesquita", "female", "Brazil", "BR", 2, black_belt.id, 16, 1890, 1870, 1910, 50, 44, 6, 0, 20),
            ("Ffion", "Davies", "female", "United Kingdom", "GB", 5, black_belt.id, 12, 1860, 1840, 1880, 38, 32, 6, 0, 14),
            ("Nathiely", "de Jesus", "female", "Brazil", "BR", 3, black_belt.id, 14, 1845, 1830, 1860, 42, 36, 6, 0, 16),
            ("Brianna", "Ste-Marie", "female", "Canada", "CA", 5, brown_belt.id, 8, 1780, 1760, 1800, 28, 24, 4, 0, 10),
            ("Roberto", "Jimenez", "male", "United States", "US", 1, black_belt.id, 8, 1910, 1890, 1930, 36, 30, 6, 0, 12),
            ("Levi", "Jones-Leary", "male", "Australia", "AU", 1, black_belt.id, 10, 1880, 1860, 1900, 34, 28, 6, 0, 14),
            ("Eoghan", "O'Flanagan", "male", "Ireland", "IE", 5, purple_belt.id, 5, 1520, 1500, 1540, 18, 14, 4, 0, 6),
            ("Tainan", "Dalpra", "male", "Brazil", "BR", 2, black_belt.id, 10, 1930, 1910, 1950, 40, 35, 5, 0, 16),
            ("Tommy", "Langaker", "male", "Norway", "NO", 2, black_belt.id, 10, 1870, 1850, 1890, 32, 27, 5, 0, 10),
        ]

        athletes = []
        for fn, ln, gender, country, cc, gym_idx, belt_id, years, elo, gi, nogi, matches, wins, losses, draws, subs in athletes_data:
            a = Athlete(
                first_name=fn, last_name=ln, display_name=f"{fn} {ln}",
                gender=gender, country=country, country_code=cc,
                sport_id=bjj.id, gym_id=gyms[gym_idx].id, belt_rank_id=belt_id,
                years_training=years, elo_rating=elo, gi_rating=gi, nogi_rating=nogi,
                peak_rating=elo, total_matches=matches, wins=wins, losses=losses,
                draws=draws, submissions=subs, is_verified=True,
            )
            athletes.append(a)
        db.add_all(athletes)
        await db.flush()

        # Update gym member counts
        for gym in gyms:
            count_result = await db.execute(
                select(Athlete).where(Athlete.gym_id == gym.id)
            )
            members = count_result.scalars().all()
            gym.member_count = len(members)
            if members:
                gym.avg_rating = round(sum(m.elo_rating for m in members) / len(members), 1)

        # --- Events ---
        events_data = [
            ("ADCC World Championships 2024", "adcc-worlds-2024", date(2024, 8, 17), date(2024, 8, 18), "ADCC", EventTier.ELITE, "Las Vegas", "United States", "US", False, True, "adcc", 1.6),
            ("IBJJF World Championship 2024", "ibjjf-worlds-2024", date(2024, 6, 1), date(2024, 6, 9), "IBJJF", EventTier.ELITE, "Anaheim", "United States", "US", True, False, "ibjjf", 1.6),
            ("AJP Abu Dhabi Grand Slam 2024", "ajp-adgs-2024", date(2024, 4, 20), date(2024, 4, 21), "AJP", EventTier.INTERNATIONAL, "Abu Dhabi", "UAE", "AE", True, True, "ajp", 1.3),
            ("Grappling Industries NYC 2024", "gi-nyc-2024", date(2024, 3, 15), None, "Grappling Industries", EventTier.REGIONAL, "New York", "United States", "US", True, True, "grappling_industries", 0.8),
            ("NAGA Chicago 2024", "naga-chicago-2024", date(2024, 2, 10), None, "NAGA", EventTier.REGIONAL, "Chicago", "United States", "US", True, True, "naga", 0.8),
            ("Polaris Invitational 24", "polaris-24", date(2024, 5, 18), None, "Polaris", EventTier.INTERNATIONAL, "London", "United Kingdom", "GB", False, True, "polaris", 1.3),
        ]

        events = []
        for name, slug, ed, end, org, tier, city, country, cc, gi, nogi, src, kf in events_data:
            e = Event(
                name=name, slug=slug, event_date=ed, end_date=end,
                organizer=org, tier=tier, city=city, country=country, country_code=cc,
                is_gi=gi, is_nogi=nogi, source=src, k_factor_multiplier=kf,
                is_published=True, matches_imported=True,
            )
            events.append(e)
        db.add_all(events)
        await db.flush()

        # --- Sample Matches ---
        elo = EloEngine()
        sample_matches = [
            (0, 2, "submission", "RNC", False, False, "Final", 0),       # Gordon vs Pena at ADCC
            (6, 7, "points", None, False, False, "Final", 0),            # Mica vs Kade at ADCC
            (3, 5, "submission", "Collar Choke", False, False, "Semi-Final", 0),  # Meregali vs Kaynan at ADCC
            (0, 1, "points", None, False, True, "Final", 1),             # Gordon vs Galvao at Worlds
            (18, 2, "submission", "Armbar", False, True, "Final", 1),    # Tainan vs Pena at Worlds
            (10, 11, "points", None, False, True, "Final", 1),           # Gabi vs Beatriz at Worlds
        ]

        for w_idx, l_idx, outcome, sub_type, is_draw, is_gi, round_name, event_idx in sample_matches:
            winner = athletes[w_idx]
            loser = athletes[l_idx]
            event = events[event_idx]

            match = Match(
                event_id=event.id,
                winner_id=winner.id,
                loser_id=loser.id,
                outcome=MatchOutcome(outcome),
                is_draw=is_draw,
                submission_type=sub_type,
                is_gi=is_gi,
                round_name=round_name,
                winner_elo_before=winner.elo_rating,
                loser_elo_before=loser.elo_rating,
                elo_calculated=True,
                is_verified=True,
            )
            db.add(match)

        await db.commit()
        print("Database seeded successfully!")
        print(f"  - {len(athletes)} athletes")
        print(f"  - {len(gyms)} gyms")
        print(f"  - {len(events)} events")
        print(f"  - {len(sample_matches)} sample matches")
        print(f"  - Admin: admin@csrankings.com / admin123456")


if __name__ == "__main__":
    asyncio.run(seed())
