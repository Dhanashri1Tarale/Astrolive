cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000-- AstroLive Journey - PostgreSQL schema
-- This mirrors the SQLAlchemy models in backend/app/models.py.
-- Not required for local development (SQLite is used by default via
-- DATABASE_URL in backend/.env) -- use this if you want to run against
-- PostgreSQL directly, e.g. via docker-compose.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    is_demo BOOLEAN DEFAULT FALSE,
    birth_date VARCHAR,
    zodiac_sign VARCHAR,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS astrologers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    specialty VARCHAR NOT NULL,
    bio TEXT DEFAULT '',
    experience_years INTEGER DEFAULT 5,
    rating FLOAT DEFAULT 4.8,
    reviews_count INTEGER DEFAULT 120,
    price_per_session INTEGER DEFAULT 499,
    avatar_emoji VARCHAR DEFAULT '🔮',
    languages JSONB DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    astrologer_id UUID NOT NULL REFERENCES astrologers(id),
    topic VARCHAR DEFAULT 'Career',
    transcript TEXT DEFAULT '',
    status VARCHAR DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id UUID NOT NULL REFERENCES consultations(id),
    summary TEXT DEFAULT '',
    key_points JSONB DEFAULT '[]',
    category VARCHAR DEFAULT 'Career',
    saved_to_memory BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    insight_id UUID REFERENCES insights(id),
    title VARCHAR NOT NULL,
    category VARCHAR DEFAULT 'Career',
    description TEXT DEFAULT '',
    progress INTEGER DEFAULT 0,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID NOT NULL REFERENCES goals(id),
    title VARCHAR NOT NULL,
    description TEXT DEFAULT '',
    is_completed BOOLEAN DEFAULT FALSE,
    "order" INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS important_dates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR NOT NULL,
    date VARCHAR NOT NULL,
    description TEXT DEFAULT '',
    reminder_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS journey_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS share_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    headline VARCHAR DEFAULT '',
    stats JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    message VARCHAR NOT NULL,
    type VARCHAR DEFAULT 'reminder',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_consultations_user ON consultations(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_user ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_actions_goal ON actions(goal_id);
CREATE INDEX IF NOT EXISTS idx_dates_user ON important_dates(user_id);
CREATE INDEX IF NOT EXISTS idx_events_user ON journey_events(user_id);
 