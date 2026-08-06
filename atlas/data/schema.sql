-- 六合图谱 SQLite Schema
-- Created: 2026-07-13
-- Purpose: Store lottery history + symbol mappings + prediction metadata

-- ===================
-- 1. PERIODS (期号)
-- ===================
CREATE TABLE IF NOT EXISTS periods (
    period_id        INTEGER PRIMARY KEY,         -- 如 2026192
    lottery_type     INTEGER NOT NULL,            -- 1=香港, 2=澳门
    lottery_name     TEXT NOT NULL,               -- human-readable
    draw_date        DATETIME NOT NULL,           -- 开奖时间
    fetched_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    source_domain    TEXT,                        -- 哪个源 (49tu/118tu/66852)
    raw_payload      TEXT,                        -- JSON for traceability
    UNIQUE(period_id, lottery_type)
);

CREATE INDEX IF NOT EXISTS idx_periods_date ON periods(draw_date);
CREATE INDEX IF NOT EXISTS idx_periods_type ON periods(lottery_type);

-- ===================
-- 2. NUMBERS (开奖号码)
-- ===================
CREATE TABLE IF NOT EXISTS numbers (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id        INTEGER NOT NULL,
    lottery_type     INTEGER NOT NULL,
    position         INTEGER NOT NULL,            -- 1-6=平码, 7=特码
    ball_number      INTEGER NOT NULL,            -- 01-49
    zodiac           TEXT,                        -- 鼠牛虎兔...
    wuxing           TEXT,                        -- 金木水火土
    wave_color       TEXT,                        -- 红蓝绿
    odd_even         TEXT,                        -- 单/双
    FOREIGN KEY (period_id, lottery_type)
        REFERENCES periods(period_id, lottery_type)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_numbers_period ON numbers(period_id, lottery_type);
CREATE INDEX IF NOT EXISTS idx_numbers_ball ON numbers(ball_number);
CREATE INDEX IF NOT EXISTS idx_numbers_zodiac ON numbers(zodiac);

-- ===================
-- 3. SYMBOL_MAPS (生肖/五行映射，每年一套)
-- ===================
CREATE TABLE IF NOT EXISTS symbol_maps (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    year             INTEGER NOT NULL,
    ball_number      INTEGER NOT NULL,            -- 01-49
    zodiac           TEXT NOT NULL,               -- 鼠牛虎兔...
    wuxing           TEXT NOT NULL,               -- 金木水火土
    wave_color       TEXT NOT NULL,               -- 红蓝绿
    odd_even         TEXT NOT NULL,               -- 单/双
    tian_di          TEXT,                        -- 天肖/地肖
    yin_yang         TEXT,                        -- 阴肖/阳肖
    male_female      TEXT,                        -- 男肖/女肖
    ji_xiong         TEXT,                        -- 吉肖/凶肖
    source           TEXT,
    UNIQUE(year, ball_number)
);

CREATE INDEX IF NOT EXISTS idx_symbol_year ON symbol_maps(year);

-- ===================
-- 4. PREDICTIONS (预测记录，含回测)
-- ===================
CREATE TABLE IF NOT EXISTS predictions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    period_id        INTEGER NOT NULL,
    lottery_type     INTEGER NOT NULL,
    predicted_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_name       TEXT NOT NULL,               -- bayes_l1 / bayes_l2 / markov
    top_5_balls      TEXT,                        -- JSON array
    top_5_probs      TEXT,                        -- JSON array
    full_distribution TEXT,                       -- JSON: full 49-ball probability dict
    actual_special   INTEGER,                     -- actual 特码 (filled after draw)
    hit_top_5        INTEGER,                     -- 0/1
    hit_top_10       INTEGER,                     -- 0/1
    log_loss         REAL,
    kl_vs_uniform    REAL,
    notes            TEXT
);

-- ===================
-- 5. BACKTEST_RUNS (回测记录)
-- ===================
CREATE TABLE IF NOT EXISTS backtest_runs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_name       TEXT NOT NULL,
    train_start      INTEGER,                     -- period_id
    train_end        INTEGER,
    test_periods     INTEGER,                     -- count
    metrics          TEXT,                        -- JSON: hit_rate, log_loss, lift
    config           TEXT                         -- JSON: hyperparameters
);

-- ===================
-- 6. SOURCES (抓取源状态)
-- ===================
CREATE TABLE IF NOT EXISTS sources (
    domain           TEXT PRIMARY KEY,
    first_seen       DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen        DATETIME,
    status           TEXT DEFAULT 'active',       -- active / dead / blocked
    notes            TEXT
);