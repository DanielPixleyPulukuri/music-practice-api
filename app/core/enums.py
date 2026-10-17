from enum import Enum


class SongKey(str, Enum):
    # Major
    C = "C"
    Db = "Db"
    D = "D"
    Eb = "Eb"
    E = "E"
    F = "F"
    Gb = "Gb"
    G = "G"
    Ab = "Ab"
    A = "A"
    Bb = "Bb"
    B = "B"

    # Minor
    Cm = "Cm"
    Dbm = "Dbm"
    Dm = "Dm"
    Ebm = "Ebm"
    Em = "Em"
    Fm = "Fm"
    Gbm = "Gbm"
    Gm = "Gm"
    Abm = "Abm"
    Am = "Am"
    Bbm = "Bbm"
    Bm = "Bm"


class SongSort(str, Enum):
    id = "id"
    title = "title"
    bpm = "bpm"
    created_at = "created_at"


class PracticeSessionSort(str, Enum):
    id = "id"
    practice_date = "practice_date"
    duration = "duration"
    created_at = "created_at"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"
