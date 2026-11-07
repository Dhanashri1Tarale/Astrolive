-- Optional seed data for PostgreSQL.
--
-- Note: the app seeds itself automatically and works with either SQLite or
-- PostgreSQL -- the first call to POST /api/auth/demo (the "Try Demo Journey"
-- button) creates the 4 astrologers and the fully populated demo account
-- (consultation, AI summary, goal, actions, dates, events) via
-- backend/app/seed.py. You do not need to run this file for the demo to work.
--
-- This file is provided only if you want astrologers present before the app
-- is first opened (e.g. for inspecting the DB directly).

INSERT INTO astrologers (name, specialty, bio, experience_years, rating, reviews_count, price_per_session, avatar_emoji, languages)
VALUES
  ('Priya Sharma', 'Career & Finance', 'Vedic astrologer specializing in career transitions and financial timing.', 12, 4.9, 482, 599, '✨', '["English","Hindi"]'),
  ('Rohan Mehta', 'Love & Relationships', 'Synastry and compatibility expert helping couples navigate timing and trust.', 9, 4.8, 310, 449, '💞', '["English","Hindi","Gujarati"]'),
  ('Ananya Iyer', 'Health & Wellbeing', 'Combines Ayurveda-aligned astrology with practical wellness routines.', 7, 4.7, 198, 399, '🌿', '["English","Tamil"]'),
  ('Vikram Nair', 'Life Purpose', 'Full birth-chart readings focused on long-term life direction.', 15, 5.0, 601, 699, '🔮', '["English","Malayalam","Hindi"]')
ON CONFLICT DO NOTHING;
