-- =========================
-- Database 
-- =========================
CREATE DATABASE IF NOT EXISTS exam_scheduler


USE exam_scheduler;

-- =========================
-- Departements
-- =========================
CREATE TABLE departements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);

-- =========================
-- Formations
-- =========================
CREATE TABLE formations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    dept_id INT NOT NULL,
    nb_modules INT NOT NULL,

    CONSTRAINT fk_formation_departement
        FOREIGN KEY (dept_id)
        REFERENCES departements(id)
        ON DELETE CASCADE
);

-- =========================
-- Etudiants
-- =========================
CREATE TABLE etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    formation_id INT NOT NULL,
    promo VARCHAR(10) NOT NULL,

    CONSTRAINT fk_etudiant_formation
        FOREIGN KEY (formation_id)
        REFERENCES formations(id)
        ON DELETE CASCADE
);

-- =========================
-- Modules
-- =========================
CREATE TABLE modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    credits INT NOT NULL,
    formation_id INT NOT NULL,
    pre_req_id INT NULL,

    CONSTRAINT fk_module_formation
        FOREIGN KEY (formation_id)
        REFERENCES formations(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_module_prerequis
        FOREIGN KEY (pre_req_id)
        REFERENCES modules(id)
        ON DELETE SET NULL,

    CONSTRAINT check_credits_positive
        CHECK (credits > 0)
);

-- =========================
-- Professeurs
-- =========================
CREATE TABLE professeurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    dept_id INT NOT NULL,
    specialite VARCHAR(150) NOT NULL,

    CONSTRAINT fk_professeur_departement
        FOREIGN KEY (dept_id)
        REFERENCES departements(id)
        ON DELETE CASCADE
);

-- =========================
-- Lieu Examen
-- =========================
CREATE TABLE lieu_examen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    capacite INT NOT NULL,
    type VARCHAR(50) NOT NULL,  -- amphi / salle / labo
    batiment VARCHAR(100) NOT NULL,

);

-- =========================
-- Inscriptions (Many-to-Many)
-- =========================
CREATE TABLE inscriptions (
    etudiant_id INT NOT NULL,
    module_id INT NOT NULL,
    note INT NULL,

    PRIMARY KEY (etudiant_id, module_id),

    CONSTRAINT fk_inscription_etudiant
        FOREIGN KEY (etudiant_id)
        REFERENCES etudiants(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_inscription_module
        FOREIGN KEY (module_id)
        REFERENCES modules(id)
        ON DELETE CASCADE
);

-- =========================
-- Examens
-- =========================
CREATE TABLE examens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    prof_id INT NOT NULL,
    salle_id INT NOT NULL,
    date_heure DATETIME NOT NULL,
    duree_minutes INT NOT NULL,

    CONSTRAINT fk_examen_module
        FOREIGN KEY (module_id)
        REFERENCES modules(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_examen_professeur
        FOREIGN KEY (prof_id)
        REFERENCES professeurs(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_examen_salle
        FOREIGN KEY (salle_id)
        REFERENCES lieu_examen(id)
        ON DELETE CASCADE,

    CONSTRAINT check_duree_positive
        CHECK (duree_minutes > 0)
);

-- =========================================
-- Indexes (Performance)
-- =========================================
CREATE INDEX idx_exams_date ON examenss(date_heure);
CREATE INDEX idx_exams_professor ON examens(prof_id);
CREATE INDEX idx_exams_room ON examens(sall_id);
CREATE INDEX idx_enrollments_module ON inscriptions(module_id);
CREATE INDEX idx_stu_exam ON inscriptions(etudiant_id, module_id);