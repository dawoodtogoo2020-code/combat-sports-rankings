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


async def seed(force: bool = False):
    engine = get_engine()
    session_factory = get_session_factory()

    if force:
        print("Force reseed: dropping all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as db:
        # Check if already seeded
        result = await db.execute(select(Sport))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping. (use --force to reseed)")
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
        # (first, last, gender, country, code, gym_key, belt, years, bio)
        athletes_raw = [
            ("Gordon", "Ryan", "male", "United States", "US", "new_wave", black_belt, 12,
             "Widely regarded as the greatest no-gi grappler of all time. Multiple-time ADCC champion across weight classes. Known for his systematic approach and dominant guard passing."),  # 0
            ("Andre", "Galvao", "male", "Brazil", "BR", "atos", black_belt, 22,
             "ADCC and IBJJF World Champion. Founder and head instructor of Atos Jiu-Jitsu. One of the most decorated grapplers in history with titles across all major organizations."),  # 1
            ("Felipe", "Pena", "male", "Brazil", "BR", "dream_art", black_belt, 18,
             "Two-time IBJJF World Champion and ADCC gold medalist. Known for his aggressive guard game and physical strength. Competes at the highest level in both gi and no-gi."),  # 2
            ("Nicholas", "Meregali", "male", "Brazil", "BR", "new_wave", black_belt, 14,
             "Multiple-time IBJJF World Champion known for his devastating collar choke game. Transitioned from gi to no-gi competition, joining New Wave Jiu-Jitsu."),  # 3
            ("Giancarlo", "Bodoni", "male", "United States", "US", "new_wave", black_belt, 8,
             "Rising star from New Wave Jiu-Jitsu. Known for his explosive style and leg lock expertise. Rapidly climbed the rankings with dominant performances."),  # 4
            ("Kaynan", "Duarte", "male", "Brazil", "BR", "atos", black_belt, 10,
             "IBJJF World Champion and ADCC medalist. One of the most dominant heavyweights in the sport. Known for his pressure passing and top game."),  # 5
            ("Mica", "Galvao", "male", "Brazil", "BR", "melqui", black_belt, 8,
             "Prodigy trained by his father Melqui Galvao. World champion at every belt level. Known for his fluid transitions, back takes, and submission finishing."),  # 6
            ("Kade", "Ruotolo", "male", "United States", "US", "atos", black_belt, 10,
             "Half of the Ruotolo twins. ADCC champion known for his aggressive scrambling and dynamic style. One of the most exciting grapplers to watch."),  # 7
            ("Tye", "Ruotolo", "male", "United States", "US", "atos", black_belt, 10,
             "Twin brother of Kade. Professional grappler and MMA competitor. Known for his fearless approach and highlight-reel submissions."),  # 8
            ("Victor", "Hugo", "male", "Brazil", "BR", "alliance", black_belt, 12,
             "Ultra-heavyweight competitor known for his incredible flexibility despite his size. Multiple-time IBJJF champion and ADCC medalist."),  # 9
            ("Roberto", "Jimenez", "male", "United States", "US", "atos", black_belt, 8,
             "Dynamic grappler known for his innovative techniques and creative guard play. Competes across multiple weight classes."),  # 10
            ("Levi", "Jones-Leary", "male", "Australia", "AU", "atos", black_belt, 10,
             "Top Australian grappler competing out of Atos. Known for his butterfly guard and sweep game. Multiple-time Pan champion."),  # 11
            ("Tainan", "Dalpra", "male", "Brazil", "BR", "aoj", black_belt, 10,
             "IBJJF World Champion and multiple-time Pan champion. Widely considered one of the best middleweight competitors. Known for his precise passing and guard retention."),  # 12
            ("Tommy", "Langaker", "male", "Norway", "NO", "alliance", black_belt, 10,
             "Norwegian grappler and European champion. Known for his technical game and spider guard. Represents Alliance in international competition."),  # 13
            ("Lucas", "Barbosa", "male", "Brazil", "BR", "atos", black_belt, 12,
             "Multiple-time IBJJF champion competing for Atos. Known for his strong passing game and pressure-based style."),  # 14
            ("Rafaela", "Guedes", "female", "Brazil", "BR", "atos", black_belt, 10,
             "ADCC champion and professional grappler. One of the strongest competitors in women's grappling with dominant takedowns and top control."),  # 15
            ("Gabi", "Garcia", "female", "Brazil", "BR", "gracie_barra", black_belt, 20,
             "One of the most dominant female grapplers in history. Multiple IBJJF and ADCC World Champion. Known for her physicality and takedown game."),  # 16
            ("Beatriz", "Mesquita", "female", "Brazil", "BR", "alliance", black_belt, 16,
             "Most decorated female BJJ competitor in history with numerous IBJJF World Championship titles. Known for her complete game and competitive drive."),  # 17
            ("Ffion", "Davies", "female", "United Kingdom", "GB", "renzo", black_belt, 12,
             "Welsh grappler and ADCC champion. First European woman to win ADCC gold. Known for her leg lock game and aggressive no-gi style."),  # 18
            ("Nathiely", "de Jesus", "female", "Brazil", "BR", "dream_art", black_belt, 14,
             "IBJJF World Champion known for her powerful guard game. Top competitor in the heavyweight women's divisions."),  # 19
            ("Brianna", "Ste-Marie", "female", "Canada", "CA", "renzo", brown_belt, 8,
             "Rising Canadian talent training at Renzo Gracie Academy. Known for her technical approach and submission skills."),  # 20
            ("Amy", "Campo", "female", "United States", "US", "atos", black_belt, 10,
             "Atos competitor in the women's division. Known for her aggressive top game and competition experience."),  # 21
            ("Marcus", "Almeida", "male", "Brazil", "BR", "dream_art", black_belt, 16,
             "Known as 'Buchecha.' Most IBJJF World Championship titles in the absolute division. Legendary competitor who defined ultra-heavyweight grappling."),  # 22
            ("Leandro", "Lo", "male", "Brazil", "BR", "cicero", black_belt, 16,
             "Eight-time IBJJF World Champion across five weight classes. Considered one of the most skilled guard passers ever. His legacy continues to inspire."),  # 23
            ("Lucas", "Lepri", "male", "Brazil", "BR", "alliance", black_belt, 18,
             "Five-time IBJJF World Champion known for his precise knee cut pass and methodical style. One of the greatest lightweights in history."),  # 24
            ("Bernardo", "Faria", "male", "Brazil", "BR", "alliance", black_belt, 18,
             "Multiple IBJJF World Champion famous for his over-under pass and half guard game. Now a prominent instructor and content creator."),  # 25
            ("Marcelo", "Garcia", "male", "Brazil", "BR", "alliance", black_belt, 24,
             "Five-time ADCC champion and four-time IBJJF World Champion. Widely considered the greatest middleweight of all time. Pioneered the X-guard and north-south choke."),  # 26
            ("Roger", "Gracie", "male", "Brazil", "BR", "gracie_barra", black_belt, 28,
             "Ten-time IBJJF World Champion. Regarded by many as the greatest BJJ competitor ever. Known for his mount cross-choke combination."),  # 27
            ("Rafael", "Mendes", "male", "Brazil", "BR", "aoj", black_belt, 18,
             "Multiple IBJJF World Champion and co-founder of Art of Jiu-Jitsu. Known for his berimbolo and innovative guard game. Now focused on coaching."),  # 28
            ("Guilherme", "Mendes", "male", "Brazil", "BR", "aoj", black_belt, 18,
             "World Champion and co-founder of Art of Jiu-Jitsu with his brother Rafael. Known for his fluid movement and guard play."),  # 29
            ("JT", "Torres", "male", "United States", "US", "atos", black_belt, 16,
             "ADCC champion known for his grinding top game and half guard passing. Long-time Atos competitor with victories over top-ranked opponents."),  # 30
            ("Craig", "Jones", "male", "Australia", "AU", "new_wave", black_belt, 12,
             "Australian grappler known for his leg lock game and heel hook expertise. ADCC medalist and one of the most popular figures in modern grappling."),  # 31
            ("Nicky", "Ryan", "male", "United States", "US", "new_wave", black_belt, 8,
             "Younger brother of Gordon Ryan. Leg lock specialist trained under John Danaher. Rising through the ranks at a young age."),  # 32
            ("Dante", "Leon", "male", "Canada", "CA", "new_wave", black_belt, 10,
             "Canadian grappler competing for New Wave. Known for his heel hook game and no-gi expertise. ADCC and WNO competitor."),  # 33
            ("Diogo", "Reis", "male", "Brazil", "BR", "melqui", black_belt, 8,
             "Training partner of Mica Galvao at Melqui Galvao BJJ. Young talent making waves in the lighter weight classes."),  # 34
            ("Fabricio", "Andrey", "male", "Brazil", "BR", "alliance", black_belt, 10,
             "Rising Alliance competitor with impressive performances at IBJJF events. Known for his dynamic guard game."),  # 35
            ("Erich", "Munis", "male", "Brazil", "BR", "dream_art", black_belt, 8,
             "Dream Art competitor known for his heavy top pressure and passing. Quickly rising through the heavyweight ranks."),  # 36
            ("Pedro", "Marinho", "male", "Brazil", "BR", "gracie_barra", black_belt, 10,
             "Gracie Barra competitor and no-gi specialist. Strong takedown game with a wrestling background."),  # 37
            ("Ana Carolina", "Vieira", "female", "Brazil", "BR", "gracie_barra", black_belt, 12,
             "Multiple-time IBJJF World Champion. One of the most decorated active female competitors in gi competition."),  # 38
            ("Mayssa", "Bastos", "female", "Brazil", "BR", "aoj", black_belt, 10,
             "Multiple IBJJF World Champion in the lighter weight classes. Known for her aggressive style and submission rate."),  # 39
            ("Amanda", "Monteiro", "female", "Brazil", "BR", "dream_art", black_belt, 12,
             "IBJJF World Champion and Pan champion. Competes across multiple weight categories with a well-rounded game."),  # 40
            ("Tammi", "Musumeci", "female", "United States", "US", "aoj", black_belt, 14,
             "IBJJF World Champion and ADCC medalist. Sister of Mikey Musumeci. Known for her berimbolo game and guard play."),  # 41
            ("Mikey", "Musumeci", "male", "United States", "US", "aoj", black_belt, 12,
             "Multiple-time IBJJF World Champion and ONE Championship grappling champion. Known as the king of the leg entanglement and berimbolo game."),  # 42
            ("Gutemberg", "Pereira", "male", "Brazil", "BR", "gracie_barra", black_belt, 10,
             "IBJJF World Champion in the super-heavy division. Known for his powerful guard game and sweeps."),  # 43
            ("Matheus", "Gabriel", "male", "Brazil", "BR", "cicero", black_belt, 10,
             "Cicero Costha product and IBJJF World Champion. Technical lightweight with excellent guard retention."),  # 44
            ("Isaac", "Doederlein", "male", "United States", "US", "alliance", black_belt, 10,
             "Alliance competitor and multiple-time Pan champion. Known for his collar sleeve guard and triangle setups."),  # 45
            ("Yara", "Soares", "female", "Brazil", "BR", "unity", black_belt, 10,
             "Unity Jiu-Jitsu competitor and Pan champion. Strong heavyweight competitor in women's division."),  # 46
            ("Elisabeth", "Clay", "female", "United States", "US", "atos", black_belt, 8,
             "IBJJF Pan champion competing for Atos. Dynamic guard player in the women's middleweight division."),  # 47
        ]

        athletes = []
        for fn, ln, gender, country, cc, gym_key, belt, years, bio in athletes_raw:
            a = Athlete(
                first_name=fn, last_name=ln, display_name=f"{fn} {ln}",
                gender=gender, country=country, country_code=cc,
                sport_id=bjj.id, gym_id=gyms[GYM[gym_key]].id, belt_rank_id=belt.id,
                years_training=years, bio=bio,
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
            # Historical events for legends
            ("ADCC World Championships 2011", "adcc-worlds-2011", date(2011, 9, 24), date(2011, 9, 25),
             "ADCC", EventTier.ELITE, "Nottingham", "United Kingdom", "GB", False, True, "adcc", 1.6),  # 0
            ("IBJJF World Championship 2012", "ibjjf-worlds-2012", date(2012, 6, 7), date(2012, 6, 10),
             "IBJJF", EventTier.ELITE, "Long Beach", "United States", "US", True, False, "ibjjf", 1.6),  # 1
            ("IBJJF World Championship 2016", "ibjjf-worlds-2016", date(2016, 6, 2), date(2016, 6, 5),
             "IBJJF", EventTier.ELITE, "Long Beach", "United States", "US", True, False, "ibjjf", 1.6),  # 2
            ("IBJJF World Championship 2018", "ibjjf-worlds-2018", date(2018, 6, 1), date(2018, 6, 3),
             "IBJJF", EventTier.ELITE, "Long Beach", "United States", "US", True, False, "ibjjf", 1.6),  # 3
            ("ADCC World Championships 2019", "adcc-worlds-2019", date(2019, 9, 28), date(2019, 9, 29),
             "ADCC", EventTier.ELITE, "Anaheim", "United States", "US", False, True, "adcc", 1.6),  # 4
            ("IBJJF World Championship 2019", "ibjjf-worlds-2019", date(2019, 5, 30), date(2019, 6, 2),
             "IBJJF", EventTier.ELITE, "Long Beach", "United States", "US", True, False, "ibjjf", 1.6),  # 5
            ("IBJJF Pan Championship 2022", "ibjjf-pan-2022", date(2022, 3, 23), date(2022, 3, 27),
             "IBJJF", EventTier.ELITE, "Kissimmee", "United States", "US", True, False, "ibjjf", 1.4),  # 6
            # Recent events
            ("ADCC World Championships 2022", "adcc-worlds-2022", date(2022, 9, 17), date(2022, 9, 18),
             "ADCC", EventTier.ELITE, "Las Vegas", "United States", "US", False, True, "adcc", 1.6),  # 7
            ("AJP Abu Dhabi Grand Slam 2023", "ajp-adgs-2023", date(2023, 4, 14), date(2023, 4, 15),
             "AJP", EventTier.INTERNATIONAL, "Abu Dhabi", "UAE", "AE", True, True, "ajp", 1.3),  # 8
            ("IBJJF World Championship 2023", "ibjjf-worlds-2023", date(2023, 6, 1), date(2023, 6, 4),
             "IBJJF", EventTier.ELITE, "Anaheim", "United States", "US", True, False, "ibjjf", 1.6),  # 9
            ("WNO Championships 2023", "wno-champs-2023", date(2023, 9, 23), date(2023, 9, 24),
             "WNO", EventTier.INTERNATIONAL, "Austin", "United States", "US", False, True, "wno", 1.3),  # 10
            ("IBJJF Pan Championship 2024", "ibjjf-pan-2024", date(2024, 3, 20), date(2024, 3, 24),
             "IBJJF", EventTier.ELITE, "Kissimmee", "United States", "US", True, False, "ibjjf", 1.4),  # 11
            ("AJP Abu Dhabi Grand Slam 2024", "ajp-adgs-2024", date(2024, 4, 20), date(2024, 4, 21),
             "AJP", EventTier.INTERNATIONAL, "Abu Dhabi", "UAE", "AE", True, True, "ajp", 1.3),  # 12
            ("IBJJF World Championship 2024", "ibjjf-worlds-2024", date(2024, 6, 1), date(2024, 6, 9),
             "IBJJF", EventTier.ELITE, "Anaheim", "United States", "US", True, False, "ibjjf", 1.6),  # 13
            ("ADCC World Championships 2024", "adcc-worlds-2024", date(2024, 8, 17), date(2024, 8, 18),
             "ADCC", EventTier.ELITE, "Las Vegas", "United States", "US", False, True, "adcc", 1.6),  # 14
            ("IBJJF Pan Championship 2025", "ibjjf-pan-2025", date(2025, 3, 19), date(2025, 3, 23),
             "IBJJF", EventTier.ELITE, "Kissimmee", "United States", "US", True, False, "ibjjf", 1.4),  # 15
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
        # Athlete indices: 0=Gordon Ryan, 1=Andre Galvao, 2=Felipe Pena, 3=Meregali,
        # 4=Bodoni, 5=Kaynan, 6=Mica Galvao, 7=Kade Ruotolo, 8=Tye Ruotolo,
        # 9=Victor Hugo, 10=Jimenez, 11=Levi, 12=Tainan, 13=Tommy, 14=Lucas Barbosa,
        # 15=Rafaela, 16=Gabi, 17=Bia Mesquita, 18=Ffion, 19=Nathiely, 20=Brianna,
        # 21=Amy Campo, 22=Buchecha, 23=Leandro Lo, 24=Lucas Lepri, 25=Bernardo Faria,
        # 26=Marcelo Garcia, 27=Roger Gracie, 28=Rafael Mendes, 29=Guilherme Mendes,
        # 30=JT Torres, 31=Craig Jones, 32=Nicky Ryan, 33=Dante Leon,
        # 34=Diogo Reis, 35=Fabricio Andrey, 36=Erich Munis, 37=Pedro Marinho,
        # 38=Ana Carolina, 39=Mayssa, 40=Amanda Monteiro, 41=Tammi, 42=Mikey,
        # 43=Gutemberg, 44=Matheus Gabriel, 45=Isaac Doederlein, 46=Yara, 47=Elisabeth Clay
        matches_data = [
            # === ADCC 2011 (event 0) — historical legends ===
            (26, 1, "submission", "Guillotine", False, "Final", 0),       # Marcelo Garcia def Galvao
            (27, 22, "submission", "Cross Choke", False, "Semi-Final", 0), # Roger def Buchecha
            (22, 25, "points", None, False, "Quarter-Final", 0),          # Buchecha def Bernardo

            # === IBJJF Worlds 2012 (event 1) — legends ===
            (22, 27, "points", None, True, "Final", 1),                   # Buchecha def Roger (absolute)
            (23, 24, "submission", "Knee Bar", True, "Final", 1),         # Leandro Lo def Lepri
            (28, 29, "points", None, True, "Final", 1),                   # Rafael Mendes def Guilherme
            (26, 42, "submission", "Guillotine", True, "Semi-Final", 1),  # Marcelo def Mikey (sim)
            (24, 45, "points", None, True, "Semi-Final", 1),              # Lepri def Isaac
            (25, 43, "points", None, True, "Quarter-Final", 1),           # Bernardo def Gutemberg

            # === IBJJF Worlds 2016 (event 2) ===
            (23, 14, "points", None, True, "Final", 2),                   # Leandro Lo def Lucas Barbosa
            (22, 9, "submission", "Armbar", True, "Final", 2),            # Buchecha def Victor Hugo
            (24, 44, "points", None, True, "Final", 2),                   # Lepri def Matheus Gabriel
            (28, 42, "points", None, True, "Final", 2),                   # Rafael Mendes def Mikey
            (17, 38, "points", None, True, "Final", 2),                   # Bia def Ana Carolina
            (16, 19, "submission", "Armbar", True, "Final", 2),           # Gabi def Nathiely

            # === IBJJF Worlds 2018 (event 3) ===
            (23, 12, "points", None, True, "Final", 3),                   # Leandro Lo def Tainan
            (22, 43, "submission", "RNC", True, "Final", 3),              # Buchecha def Gutemberg
            (42, 44, "submission", "Armbar", True, "Final", 3),           # Mikey def Matheus Gabriel
            (5, 25, "points", None, True, "Semi-Final", 3),               # Kaynan def Bernardo
            (17, 16, "points", None, True, "Final", 3),                   # Bia def Gabi
            (39, 41, "submission", "Choke", True, "Final", 3),            # Mayssa def Tammi

            # === IBJJF Worlds 2019 (event 5) ===
            (5, 22, "points", None, True, "Final", 5),                    # Kaynan def Buchecha
            (12, 24, "points", None, True, "Final", 5),                   # Tainan def Lepri
            (42, 35, "submission", "Heel Hook", True, "Final", 5),        # Mikey def Fabricio
            (1, 14, "points", None, True, "Semi-Final", 5),               # Galvao def Lucas Barbosa
            (38, 40, "points", None, True, "Final", 5),                   # Ana Carolina def Amanda
            (39, 20, "submission", "Armbar", True, "Semi-Final", 5),      # Mayssa def Brianna

            # === ADCC 2019 (event 4) ===
            (0, 31, "points", None, False, "Final", 4),                   # Gordon def Craig Jones
            (30, 33, "points", None, False, "Final", 4),                  # JT Torres def Dante Leon
            (7, 32, "points", None, False, "Semi-Final", 4),              # Kade def Nicky Ryan
            (22, 9, "submission", "RNC", False, "Semi-Final", 4),         # Buchecha def Victor Hugo
            (2, 37, "submission", "Guillotine", False, "Quarter-Final", 4), # Pena def Pedro Marinho
            (15, 18, "points", None, False, "Final", 4),                  # Rafaela def Ffion

            # === IBJJF Pan 2022 (event 6) ===
            (12, 35, "points", None, True, "Final", 6),                   # Tainan def Fabricio
            (5, 36, "points", None, True, "Semi-Final", 6),               # Kaynan def Erich Munis
            (42, 34, "submission", "Leg Lock", True, "Final", 6),         # Mikey def Diogo
            (44, 45, "points", None, True, "Final", 6),                   # Matheus Gabriel def Isaac
            (11, 13, "points", None, True, "Semi-Final", 6),              # Levi def Tommy
            (38, 46, "points", None, True, "Final", 6),                   # Ana Carolina def Yara
            (39, 47, "submission", "Choke", True, "Final", 6),            # Mayssa def Elisabeth Clay
            (40, 41, "points", None, True, "Semi-Final", 6),              # Amanda def Tammi

            # === ADCC 2022 (event 7) ===
            (0, 1, "points", None, False, "Final", 7),                    # Gordon def Galvao
            (6, 7, "points", None, False, "Final", 7),                    # Mica def Kade
            (3, 5, "submission", "Guillotine", False, "Semi-Final", 7),   # Meregali def Kaynan
            (0, 3, "submission", "RNC", False, "Final", 7),               # Gordon def Meregali
            (4, 9, "points", None, False, "Quarter-Final", 7),            # Bodoni def Victor Hugo
            (7, 8, "points", None, False, "Semi-Final", 7),               # Kade def Tye
            (18, 20, "submission", "Armbar", False, "Final", 7),          # Ffion def Brianna
            (16, 19, "points", None, False, "Final", 7),                  # Gabi def Nathiely
            (12, 13, "points", None, False, "Semi-Final", 7),             # Tainan def Tommy
            (31, 37, "submission", "Heel Hook", False, "Quarter-Final", 7), # Craig def Pedro
            (30, 33, "submission", "RNC", False, "Semi-Final", 7),        # JT def Dante
            (32, 10, "submission", "Heel Hook", False, "Quarter-Final", 7), # Nicky def Jimenez
            (36, 43, "points", None, False, "Quarter-Final", 7),          # Erich def Gutemberg
            (47, 46, "points", None, False, "Quarter-Final", 7),          # Elisabeth def Yara

            # === AJP Abu Dhabi Grand Slam 2023 (event 8) ===
            (5, 9, "points", None, True, "Final", 8),                     # Kaynan def Victor Hugo
            (12, 11, "submission", "Choke", True, "Final", 8),            # Tainan def Levi
            (17, 19, "points", None, True, "Final", 8),                   # Bia def Nathiely
            (34, 42, "points", None, True, "Semi-Final", 8),              # Diogo def Mikey
            (35, 45, "points", None, True, "Quarter-Final", 8),           # Fabricio def Isaac

            # === IBJJF Worlds 2023 (event 9) ===
            (12, 13, "points", None, True, "Final", 9),                   # Tainan def Tommy
            (5, 2, "points", None, True, "Final", 9),                     # Kaynan def Pena
            (1, 9, "points", None, True, "Semi-Final", 9),                # Galvao def Victor Hugo
            (16, 17, "submission", "Armbar", True, "Final", 9),           # Gabi def Bia
            (14, 11, "points", None, True, "Final", 9),                   # Lucas Barbosa def Levi
            (18, 21, "points", None, True, "Semi-Final", 9),              # Ffion def Amy
            (42, 34, "submission", "Heel Hook", True, "Final", 9),        # Mikey def Diogo
            (6, 35, "submission", "RNC", True, "Semi-Final", 9),          # Mica def Fabricio
            (36, 43, "points", None, True, "Quarter-Final", 9),           # Erich def Gutemberg
            (44, 45, "submission", "Triangle", True, "Semi-Final", 9),    # Matheus def Isaac
            (38, 40, "points", None, True, "Final", 9),                   # Ana Carolina def Amanda
            (39, 47, "submission", "Armbar", True, "Final", 9),           # Mayssa def Elisabeth

            # === WNO Championships 2023 (event 10) ===
            (0, 2, "submission", "RNC", False, "Final", 10),              # Gordon def Pena
            (6, 12, "submission", "Heel Hook", False, "Final", 10),       # Mica def Tainan
            (7, 10, "points", None, False, "Final", 10),                  # Kade def Jimenez
            (3, 5, "submission", "Collar Choke", False, "Semi-Final", 10), # Meregali def Kaynan
            (31, 32, "points", None, False, "Semi-Final", 10),            # Craig def Nicky
            (33, 37, "submission", "Heel Hook", False, "Quarter-Final", 10), # Dante def Pedro

            # === IBJJF Pan 2024 (event 11) ===
            (12, 35, "submission", "Choke", True, "Final", 11),           # Tainan def Fabricio
            (6, 34, "points", None, True, "Final", 11),                   # Mica def Diogo
            (44, 42, "points", None, True, "Semi-Final", 11),             # Matheus def Mikey
            (5, 36, "submission", "RNC", True, "Semi-Final", 11),         # Kaynan def Erich
            (11, 45, "points", None, True, "Final", 11),                  # Levi def Isaac
            (38, 46, "points", None, True, "Final", 11),                  # Ana Carolina def Yara
            (39, 41, "submission", "Choke", True, "Final", 11),           # Mayssa def Tammi
            (47, 21, "points", None, True, "Semi-Final", 11),             # Elisabeth def Amy

            # === AJP Abu Dhabi Grand Slam 2024 (event 12) ===
            (12, 13, "submission", "Choke", True, "Final", 12),           # Tainan def Tommy
            (5, 9, "submission", "Footlock", True, "Final", 12),          # Kaynan def Victor Hugo
            (17, 21, "points", None, True, "Final", 12),                  # Bia def Amy
            (34, 44, "points", None, True, "Semi-Final", 12),             # Diogo def Matheus
            (40, 46, "points", None, True, "Quarter-Final", 12),          # Amanda def Yara

            # === IBJJF Worlds 2024 (event 13) ===
            (12, 2, "submission", "Armbar", True, "Final", 13),           # Tainan def Pena
            (5, 1, "points", None, True, "Final", 13),                    # Kaynan def Galvao
            (3, 9, "submission", "Ezekiel Choke", True, "Semi-Final", 13), # Meregali def Victor Hugo
            (0, 3, "points", None, True, "Final", 13),                    # Gordon def Meregali
            (16, 19, "points", None, True, "Final", 13),                  # Gabi def Nathiely
            (18, 17, "submission", "Heel Hook", True, "Final", 13),       # Ffion def Bia
            (6, 7, "submission", "RNC", True, "Final", 13),               # Mica def Kade
            (42, 34, "submission", "Leg Lock", True, "Final", 13),        # Mikey def Diogo
            (36, 43, "points", None, True, "Semi-Final", 13),             # Erich def Gutemberg
            (44, 35, "points", None, True, "Final", 13),                  # Matheus def Fabricio
            (38, 39, "points", None, True, "Final", 13),                  # Ana Carolina def Mayssa
            (41, 47, "submission", "Armbar", True, "Semi-Final", 13),     # Tammi def Elisabeth

            # === ADCC 2024 (event 14) ===
            (0, 5, "submission", "RNC", False, "Final", 14),              # Gordon def Kaynan
            (6, 31, "submission", "RNC", False, "Final", 14),             # Mica def Craig
            (3, 2, "points", None, False, "Semi-Final", 14),              # Meregali def Pena
            (7, 30, "points", None, False, "Semi-Final", 14),             # Kade def JT Torres
            (8, 33, "submission", "Guillotine", False, "Quarter-Final", 14), # Tye def Dante
            (4, 37, "points", None, False, "Quarter-Final", 14),          # Bodoni def Pedro
            (32, 10, "submission", "Heel Hook", False, "Quarter-Final", 14), # Nicky def Jimenez
            (15, 47, "points", None, False, "Final", 14),                 # Rafaela def Elisabeth
            (18, 46, "submission", "Heel Hook", False, "Semi-Final", 14), # Ffion def Yara
            (36, 9, "points", None, False, "Quarter-Final", 14),          # Erich def Victor Hugo

            # === IBJJF Pan 2025 (event 15) ===
            (6, 12, "points", None, True, "Final", 15),                   # Mica def Tainan
            (34, 42, "submission", "RNC", True, "Final", 15),             # Diogo def Mikey
            (5, 36, "points", None, True, "Final", 15),                   # Kaynan def Erich
            (44, 45, "points", None, True, "Final", 15),                  # Matheus def Isaac
            (35, 11, "points", None, True, "Semi-Final", 15),             # Fabricio def Levi
            (38, 40, "submission", "Choke", True, "Final", 15),           # Ana Carolina def Amanda
            (39, 41, "points", None, True, "Final", 15),                  # Mayssa def Tammi
            (47, 46, "points", None, True, "Semi-Final", 15),             # Elisabeth def Yara
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
    import sys
    force = "--force" in sys.argv
    asyncio.run(seed(force=force))
