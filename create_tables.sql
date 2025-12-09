-- ==========================================
-- Vision Care Database - テーブル作成SQL
-- ==========================================
-- このファイルはStep4_Backend/app/models.pyに基づいて作成されています
-- 実行日: 2025-12-09
-- ==========================================

-- データベースの作成（必要に応じて）
CREATE DATABASE IF NOT EXISTS vision_care_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vision_care_db;

-- ==========================================
-- 1. Parentテーブル（保護者）
-- ==========================================
CREATE TABLE Parent (
    parent_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    line_id VARCHAR(255) UNIQUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    last_login_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_line_id (line_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 2. Childテーブル（子供）
-- ==========================================
CREATE TABLE Child (
    child_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT,
    name VARCHAR(50),
    INDEX idx_child_id (child_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 3. Exerciseテーブル（視力トレーニング種目）
-- ==========================================
CREATE TABLE Exercise (
    exercise_id INT AUTO_INCREMENT PRIMARY KEY,
    exercise_type VARCHAR(50) NOT NULL,
    exercise_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_exercise_id (exercise_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 4. ExerciseLogテーブル（トレーニング記録）
-- ==========================================
CREATE TABLE ExerciseLog (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    exercise_id INT NOT NULL,
    exercise_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_log_id (log_id),
    INDEX idx_child_id (child_id),
    CONSTRAINT fk_exerciselog_exercise FOREIGN KEY (exercise_id) REFERENCES Exercise(exercise_id),
    CONSTRAINT unique_child_exercise_date UNIQUE (child_id, exercise_id, exercise_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 5. DistanceCheckテーブル（画面との距離チェック）
-- ==========================================
CREATE TABLE DistanceCheck (
    distance_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    check_date DATE NOT NULL,
    avg_distance_cm INT NOT NULL,
    posture_score INT DEFAULT 0,
    alert_flag BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_distance_id (distance_id),
    CONSTRAINT fk_distancecheck_child FOREIGN KEY (child_id) REFERENCES Child(child_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 6. refresh_tokensテーブル（リフレッシュトークン）
-- ==========================================
CREATE TABLE refresh_tokens (
    token_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_token_id (token_id),
    CONSTRAINT fk_refreshtoken_parent FOREIGN KEY (parent_id) REFERENCES Parent(parent_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 7. verification_codesテーブル（メール認証コード）
-- ==========================================
CREATE TABLE verification_codes (
    verification_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    code_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_verification_id (verification_id),
    INDEX idx_session_id (session_id),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 8. Settingsテーブル（設定）
-- ==========================================
CREATE TABLE Settings (
    settings_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL UNIQUE,
    child_id INT,
    voice_enabled BOOLEAN DEFAULT TRUE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_settings_id (settings_id),
    CONSTRAINT fk_settings_parent FOREIGN KEY (parent_id) REFERENCES Parent(parent_id),
    CONSTRAINT fk_settings_child FOREIGN KEY (child_id) REFERENCES Child(child_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 9. EyeTestテーブル（視力検査記録）
-- ==========================================
CREATE TABLE EyeTest (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    check_date DATE NOT NULL,
    left_eye VARCHAR(10),
    right_eye VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_test_id (test_id),
    INDEX idx_child_id (child_id),
    CONSTRAINT fk_eyetest_child FOREIGN KEY (child_id) REFERENCES Child(child_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 10. ScreenTimeテーブル（スクリーンタイム記録）
-- ==========================================
CREATE TABLE ScreenTime (
    screentime_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    total_minutes INT,
    alert_flag BOOLEAN DEFAULT FALSE,
    INDEX idx_screentime_id (screentime_id),
    INDEX idx_child_id (child_id),
    CONSTRAINT fk_screentime_child FOREIGN KEY (child_id) REFERENCES Child(child_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- 実行方法
-- ==========================================
-- ターミナルから以下のコマンドで実行できます：
-- mysql -u ユーザー名 -p < create_tables.sql
--
-- または、MySQLクライアント内で：
-- source /path/to/create_tables.sql;
-- ==========================================
