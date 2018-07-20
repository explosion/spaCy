"""
Daftar singkatan dan Akronim dari:
https://id.wiktionary.org/wiki/Wiktionary:Daftar_singkatan_dan_akronim_bahasa_Indonesia#A
"""
# coding: utf8
from __future__ import unicode_literals

from ._tokenizer_exceptions_list import ID_BASE_EXCEPTIONS
from ...symbols import ORTH, LEMMA, NORM


_exc = {}

for orth in ID_BASE_EXCEPTIONS:
    _exc[orth] = [{ORTH: orth}]

    orth_title = orth.title()
    _exc[orth_title] = [{ORTH: orth_title}]

    orth_caps = orth.upper()
    _exc[orth_caps] = [{ORTH: orth_caps}]

    orth_lower = orth.lower()
    _exc[orth_lower] = [{ORTH: orth_lower}]

    if '-' in orth:
        orth_title = '-'.join([part.title() for part in orth.split('-')])
        _exc[orth_title] = [{ORTH: orth_title}]

        orth_caps = '-'.join([part.upper() for part in orth.split('-')])
        _exc[orth_caps] = [{ORTH: orth_caps}]

for exc_data in [
    {ORTH: "CKG", LEMMA: "Cakung", NORM: "Cakung"},
    {ORTH: "CGP", LEMMA: "Grogol Petamburan", NORM: "Grogol Petamburan"},
    {ORTH: "KSU", LEMMA: "Kepulauan Seribu Utara",
     NORM: "Kepulauan Seribu Utara"},
    {ORTH: "KYB", LEMMA: "Kebayoran Baru", NORM: "Kebayoran Baru"},
    {ORTH: "TJP", LEMMA: "Tanjungpriok", NORM: "Tanjungpriok"},
    {ORTH: "TNA", LEMMA: "Tanah Abang", NORM: "Tanah Abang"},

    {ORTH: "BEK", LEMMA: "Bengkayang", NORM: "Bengkayang"},
    {ORTH: "KTP", LEMMA: "Ketapang", NORM: "Ketapang"},
    {ORTH: "MPW", LEMMA: "Mempawah", NORM: "Mempawah"},
    {ORTH: "NGP", LEMMA: "Nanga Pinoh", NORM: "Nanga Pinoh"},
    {ORTH: "NBA", LEMMA: "Ngabang", NORM: "Ngabang"},
    {ORTH: "PTK", LEMMA: "Pontianak", NORM: "Pontianak"},
    {ORTH: "PTS", LEMMA: "Putussibau", NORM: "Putussibau"},
    {ORTH: "SBS", LEMMA: "Sambas", NORM: "Sambas"},
    {ORTH: "SAG", LEMMA: "Sanggau", NORM: "Sanggau"},
    {ORTH: "SED", LEMMA: "Sekadau", NORM: "Sekadau"},
    {ORTH: "SKW", LEMMA: "Singkawang", NORM: "Singkawang"},
    {ORTH: "STG", LEMMA: "Sintang", NORM: "Sintang"},
    {ORTH: "SKD", LEMMA: "Sukadane", NORM: "Sukadane"},
    {ORTH: "SRY", LEMMA: "Sungai Raya", NORM: "Sungai Raya"},

    {ORTH: "Jan.", LEMMA: "Januari", NORM: "Januari"},
    {ORTH: "Feb.", LEMMA: "Februari", NORM: "Februari"},
    {ORTH: "Mar.", LEMMA: "Maret", NORM: "Maret"},
    {ORTH: "Apr.", LEMMA: "April", NORM: "April"},
    {ORTH: "Jun.", LEMMA: "Juni", NORM: "Juni"},
    {ORTH: "Jul.", LEMMA: "Juli", NORM: "Juli"},
    {ORTH: "Agu.", LEMMA: "Agustus", NORM: "Agustus"},
    {ORTH: "Ags.", LEMMA: "Agustus", NORM: "Agustus"},
    {ORTH: "Sep.", LEMMA: "September", NORM: "September"},
    {ORTH: "Okt.", LEMMA: "Oktober", NORM: "Oktober"},
    {ORTH: "Nov.", LEMMA: "November", NORM: "November"},
    {ORTH: "Des.", LEMMA: "Desember", NORM: "Desember"},

    {
        ORTH: "a.l.",
        LEMMA: "antara lain",
        NORM: "antara lain"},
    {
        ORTH: "a.n.",
        LEMMA: "atas nama",
        NORM: "atas nama"},
    {
        ORTH: "a.s.",
        LEMMA: "alaihi salam",
        NORM: "alaihi salam"},
    {
        ORTH: "AAI",
        LEMMA: "Asosiasi Advokat Indonesia",
        NORM: "Asosiasi Advokat Indonesia"},
    {
        ORTH: "ABG",
        LEMMA: "Anak Baru Gede",
        NORM: "Anak Baru Gede"},
    {
        ORTH: "ABRI",
        LEMMA: "Angkatan Bersenjata Republik Indonesia",
        NORM: "Angkatan Bersenjata Republik Indonesia"},
    {
        ORTH: "adm.",
        LEMMA: "administrasi",
        NORM: "administrasi"},
    {
        ORTH: "AIPTU",
        LEMMA: "Ajun Inspektur Polisi Satu",
        NORM: "Ajun Inspektur Polisi Satu"},
    {
        ORTH: "AJI",
        LEMMA: "Aliansi Jurnalis Independen",
        NORM: "Aliansi Jurnalis Independen"},
    {
        ORTH: "akad",
        LEMMA: "antarkerja antardaerah",
        NORM: "antarkerja antardaerah"},
    {
        ORTH: "AKPOL",
        LEMMA: "Akademi Polisi",
        NORM: "Akademi Polisi"},
    {
        ORTH: "amdal",
        LEMMA: "analisis mengenai dampak lingkungan",
        NORM: "analisis mengenai dampak lingkungan"},
    {
        ORTH: "angkot",
        LEMMA: "angkutan kota",
        NORM: "angkutan kota"},
    {
        ORTH: "APBD",
        LEMMA: "Anggaran Pendapatan dan Belanja Daerah",
        NORM: "Anggaran Pendapatan dan Belanja Daerah"},
    {
        ORTH: "APBN",
        LEMMA: "Anggaran Pendapatan dan Belanja Negara",
        NORM: "Anggaran Pendapatan dan Belanja Negara"},
    {
        ORTH: "ASI",
        LEMMA: "air susu ibu",
        NORM: "air susu ibu"},
    {
        ORTH: "ATM",
        LEMMA: "Anjungan Tunai Mandiri",
        NORM: "Anjungan Tunai Mandiri"},
    {
        ORTH: "Babel",
        LEMMA: "Bangka Belitung",
        NORM: "Bangka Belitung"},
    {
        ORTH: "Bappeda",
        LEMMA: "Badan Perencanaan dan Pembangunan Daerah",
        NORM: "Badan Perencanaan dan Pembangunan Daerah"},
    {
        ORTH: "Bappenas",
        LEMMA: "Badan Perencanaan dan Pembangunan Nasional",
        NORM: "Badan Perencanaan dan Pembangunan Nasional"},
    {
        ORTH: "Basarnas",
        LEMMA: "Badan SAR Nasional",
        NORM: "Badan SAR Nasional"},
    {
        ORTH: "Bawasda",
        LEMMA: "Badan Pengawas Daerah",
        NORM: "Badan Pengawas Daerah"},
    {
        ORTH: "Bawaslu",
        LEMMA: "Badan Pengawas Pemilihan Umum",
        NORM: "Badan Pengawas Pemilihan Umum"},
    {
        ORTH: "Bawasprop",
        LEMMA: "Badan Pengawas Provinsi",
        NORM: "Badan Pengawas Provinsi"},
    {
        ORTH: "BBG",
        LEMMA: "bahan bakar gas",
        NORM: "bahan bakar gas"},
    {
        ORTH: "BBM",
        LEMMA: "bahan bakar minyak",
        NORM: "bahan bakar minyak"},
    {
        ORTH: "BCA",
        LEMMA: "Bank Central Asia",
        NORM: "Bank Central Asia"},
    {
        ORTH: "BEI",
        LEMMA: "Bursa Efek Indonesia",
        NORM: "Bursa Efek Indonesia"},
    {
        ORTH: "BEJ",
        LEMMA: "Bursa Efek Jakarta",
        NORM: "Bursa Efek Jakarta"},
    {
        ORTH: "BIN",
        LEMMA: "Badan Intelijen Negara",
        NORM: "Badan Intelijen Negara"},
    {
        ORTH: "Binus",
        LEMMA: "Bina Nusantara",
        NORM: "Bina Nusantara"},
    {
        ORTH: "BLBI",
        LEMMA: "Badan Likuiditas Bank Indonesia",
        NORM: "Badan Likuiditas Bank Indonesia"},
    {
        ORTH: "BMKG",
        LEMMA: "Badan Meteorologi, Klimatologi, dan Geofisika",
        NORM: "Badan Meteorologi, Klimatologi, dan Geofisika"},
    {
        ORTH: "BNI",
        LEMMA: "Bank Negara Indonesia",
        NORM: "Bank Negara Indonesia"},
    {
        ORTH: "BNN",
        LEMMA: "Badan Narkotika Nasional",
        NORM: "Badan Narkotika Nasional"},
    {
        ORTH: "BPJS",
        LEMMA: "Badan Penyelenggara Jaminan Sosial",
        NORM: "Badan Penyelenggara Jaminan Sosial"},
    {
        ORTH: "BPKB",
        LEMMA: "Buku Pemilik Kendaraan Bermotor",
        NORM: "Buku Pemilik Kendaraan Bermotor"},
    {
        ORTH: "BPOM",
        LEMMA: "Badan Pengawasan Obat dan Makanan",
        NORM: "Badan Pengawasan Obat dan Makanan"},
    {
        ORTH: "BPPT",
        LEMMA: "Badan Pengkajian dan Penerapan Teknologi",
        NORM: "Badan Pengkajian dan Penerapan Teknologi"},
    {
        ORTH: "BPS",
        LEMMA: "Badan Pusat Statistik",
        NORM: "Badan Pusat Statistik"},
    {
        ORTH: "BRI",
        LEMMA: "Bank Rakyat Indonesia",
        NORM: "Bank Rakyat Indonesia"},
    {
        ORTH: "brimob",
        LEMMA: "brigade mobil",
        NORM: "brigade mobil"},
    {
        ORTH: "briptu",
        LEMMA: "brigadir polisi satu",
        NORM: "brigadir polisi satu"},
    {
        ORTH: "Bukopin",
        LEMMA: "Bank Umum Koperasi Indonesia",
        NORM: "Bank Umum Koperasi Indonesia"},
    {
        ORTH: "Cagub",
        LEMMA: "calon gubenur",
        NORM: "calon gubenur"},
    {
        ORTH: "cagub",
        LEMMA: "calon gubenur",
        NORM: "calon gubenur"},
    {
        ORTH: "Calhaj",
        LEMMA: "calon haji",
        NORM: "calon haji"},
    {
        ORTH: "calhaj",
        LEMMA: "calon haji",
        NORM: "calon haji"},
    {
        ORTH: "Capres",
        LEMMA: "calon presiden",
        NORM: "calon presiden"},
    {
        ORTH: "capres",
        LEMMA: "calon presiden",
        NORM: "calon presiden"},
    {
        ORTH: "Cawagub",
        LEMMA: "calon wakil gubenur",
        NORM: "calon wakil gubenur"},
    {
        ORTH: "cawagub",
        LEMMA: "calon wakil gubenur",
        NORM: "calon wakil gubenur"},
    {
        ORTH: "Cawapres",
        LEMMA: "calon wakil presiden",
        NORM: "calon wakil presiden"},
    {
        ORTH: "cawapres",
        LEMMA: "calon wakil presiden",
        NORM: "calon wakil presiden"},
    {
        ORTH: "cerpen",
        LEMMA: "cerita pendek",
        NORM: "cerita pendek"},
    {
        ORTH: "d.a.",
        LEMMA: "dengan alamat",
        NORM: "dengan alamat"},
    {
        ORTH: "DAMRI",
        LEMMA: "Djawatan Angkutan Motor Republik Indonesia",
        NORM: "Djawatan Angkutan Motor Republik Indonesia"},
    {
        ORTH: "depdagri",
        LEMMA: "Departemen Dalam Negeri",
        NORM: "Departemen Dalam Negeri"},
    {
        ORTH: "Depdagri",
        LEMMA: "Departemen Dalam Negeri",
        NORM: "Departemen Dalam Negeri"},
    {
        ORTH: "depdikbud",
        LEMMA: "Departemen Pendidikan dan Kebudayaan",
        NORM: "Departemen Pendidikan dan Kebudayaan"},
    {
        ORTH: "Depdikbud",
        LEMMA: "Departemen Pendidikan dan Kebudayaan",
        NORM: "Departemen Pendidikan dan Kebudayaan"},
    {
        ORTH: "depdiknas",
        LEMMA: "Departemen Pendidikan Nasional",
        NORM: "Departemen Pendidikan Nasional"},
    {
        ORTH: "Depdiknas",
        LEMMA: "Departemen Pendidikan Nasional",
        NORM: "Departemen Pendidikan Nasional"},
    {
        ORTH: "dephub",
        LEMMA: "Departemen Perhubungan",
        NORM: "Departemen Perhubungan"},
    {
        ORTH: "Dephub",
        LEMMA: "Departemen Perhubungan",
        NORM: "Departemen Perhubungan"},
    {
        ORTH: "dephut",
        LEMMA: "Departemen Kehutanan",
        NORM: "Departemen Kehutanan"},
    {
        ORTH: "Dephut",
        LEMMA: "Departemen Kehutanan",
        NORM: "Departemen Kehutanan"},
    {
        ORTH: "depkes",
        LEMMA: "Departemen Kesehatan",
        NORM: "Departemen Kesehatan"},
    {
        ORTH: "Depkes",
        LEMMA: "Departemen Kesehatan",
        NORM: "Departemen Kesehatan"},
    {
        ORTH: "depkeu",
        LEMMA: "Departemen Keuangan",
        NORM: "Departemen Keuangan"},
    {
        ORTH: "Depkeu",
        LEMMA: "Departemen Keuangan",
        NORM: "Departemen Keuangan"},
    {
        ORTH: "depkimpraswil",
        LEMMA: "Departemen Permukiman dan Prasarana Wilayah",
        NORM: "Departemen Permukiman dan Prasarana Wilayah"},
    {
        ORTH: "Depkimpraswil",
        LEMMA: "Departemen Permukiman dan Prasarana Wilayah",
        NORM: "Departemen Permukiman dan Prasarana Wilayah"},
    {
        ORTH: "depkominfo",
        LEMMA: "Departemen Komunikasi dan Informatika",
        NORM: "Departemen Komunikasi dan Informatika"},
    {
        ORTH: "Depkominfo",
        LEMMA: "Departemen Komunikasi dan Informatika",
        NORM: "Departemen Komunikasi dan Informatika"},
    {
        ORTH: "depkumdang",
        LEMMA: "Departemen Hukum dan Perundang-undangan",
        NORM: "Departemen Hukum dan Perundang-undangan"},
    {
        ORTH: "Depkumdang",
        LEMMA: "Departemen Hukum dan Perundang-undangan",
        NORM: "Departemen Hukum dan Perundang-undangan"},
    {
        ORTH: "depkumham",
        LEMMA: "Departemen Hukum dan Hak Asasi Manusia",
        NORM: "Departemen Hukum dan Hak Asasi Manusia"},
    {
        ORTH: "Depkumham",
        LEMMA: "Departemen Hukum dan Hak Asasi Manusia",
        NORM: "Departemen Hukum dan Hak Asasi Manusia"},
    {
        ORTH: "deplu",
        LEMMA: "Departemen Luar Negeri",
        NORM: "Departemen Luar Negeri"},
    {
        ORTH: "Deplu",
        LEMMA: "Departemen Luar Negeri",
        NORM: "Departemen Luar Negeri"},
    {
        ORTH: "depnaker",
        LEMMA: "Departemen Tenaga Kerja",
        NORM: "Departemen Tenaga Kerja"},
    {
        ORTH: "Depnaker",
        LEMMA: "Departemen Tenaga Kerja",
        NORM: "Departemen Tenaga Kerja"},
    {
        ORTH: "depnakertrans",
        LEMMA: "Departemen Tenaga Kerja dan Transmigrasi",
        NORM: "Departemen Tenaga Kerja dan Transmigrasi"},
    {
        ORTH: "Depnakertrans",
        LEMMA: "Departemen Tenaga Kerja dan Transmigrasi",
        NORM: "Departemen Tenaga Kerja dan Transmigrasi"},
    {
        ORTH: "depparbud",
        LEMMA: "Departemen Pariwisata dan Kebudayaan",
        NORM: "Departemen Pariwisata dan Kebudayaan"},
    {
        ORTH: "Depparbud",
        LEMMA: "Departemen Pariwisata dan Kebudayaan",
        NORM: "Departemen Pariwisata dan Kebudayaan"},
    {
        ORTH: "depsos",
        LEMMA: "Departemen Sosial",
        NORM: "Departemen Sosial"},
    {
        ORTH: "Depsos",
        LEMMA: "Departemen Sosial",
        NORM: "Departemen Sosial"},
    {
        ORTH: "deptamben",
        LEMMA: "Departemen Pertambangan dan Energi",
        NORM: "Departemen Pertambangan dan Energi"},
    {
        ORTH: "Deptamben",
        LEMMA: "Departemen Pertambangan dan Energi",
        NORM: "Departemen Pertambangan dan Energi"},
    {
        ORTH: "deptan",
        LEMMA: "Departemen Pertanian",
        NORM: "Departemen Pertanian"},
    {
        ORTH: "Deptan",
        LEMMA: "Departemen Pertanian",
        NORM: "Departemen Pertanian"},
    {
        ORTH: "diklat",
        LEMMA: "pendidikan dan pelatihan",
        NORM: "pendidikan dan pelatihan"},
    {
        ORTH: "Diklat",
        LEMMA: "pendidikan dan pelatihan",
        NORM: "pendidikan dan pelatihan"},
    {
        ORTH: "dikti",
        LEMMA: "Pendidikan Tinggi",
        NORM: "Pendidikan Tinggi"},
    {
        ORTH: "Dikti",
        LEMMA: "Pendidikan Tinggi",
        NORM: "Pendidikan Tinggi"},
    {
        ORTH: "dirjen",
        LEMMA: "direktur jenderal",
        NORM: "direktur jenderal"},
    {
        ORTH: "Dirjen",
        LEMMA: "direktur jenderal",
        NORM: "direktur jenderal"},
    {
        ORTH: "ditjen",
        LEMMA: "direktorat jenderal",
        NORM: "direktorat jenderal"},
    {
        ORTH: "ditjen",
        LEMMA: "direktorat jenderal",
        NORM: "direktorat jenderal"},
    {
        ORTH: "DIY",
        LEMMA: "Daerah Istimewa Yogyakarta",
        NORM: "Daerah Istimewa Yogyakarta"},
    {
        ORTH: "DKI",
        LEMMA: "Daerah Khusus Ibukota",
        NORM: "Daerah Khusus Ibukota"},
    {
        ORTH: "dkk.",
        LEMMA: "dan kawan-kawan",
        NORM: "dan kawan-kawan"},
    {
        ORTH: "dll.",
        LEMMA: "dan lain-lain",
        NORM: "dan lain-lain"},
    {
        ORTH: "DPO",
        LEMMA: "Daftar Pencarian Orang",
        NORM: "Daftar Pencarian Orang"},
    {
        ORTH: "DPP",
        LEMMA: "Dewan Pimpinan Pusat",
        NORM: "Dewan Pimpinan Pusat"},
    {
        ORTH: "DPR",
        LEMMA: "Dewan Perwakilan Rakyat",
        NORM: "Dewan Perwakilan Rakyat"},
    {
        ORTH: "DPRD",
        LEMMA: "Dewan Perwakilan Rakyat Daerah",
        NORM: "Dewan Perwakilan Rakyat Daerah"},
    {
        ORTH: "ESDM",
        LEMMA: "Energi Sumber Daya Mineral",
        NORM: "Energi Sumber Daya Mineral"},
    {
        ORTH: "ETA",
        LEMMA: "Estimate Time Of Arrived",
        NORM: "Estimate Time Of Arrived"},
    {
        ORTH: "ETD",
        LEMMA: "Estimate Time Of Departured",
        NORM: "Estimate Time Of Departured"},
    {
        ORTH: "EYD",
        LEMMA: "Ejaan yang Disempurnakan",
        NORM: "Ejaan yang Disempurnakan"},
    {
        ORTH: "GBK",
        LEMMA: "Gelora Bung Karno",
        NORM: "Gelora Bung Karno"},
    {
        ORTH: "Golkar",
        LEMMA: "Golongan Karya",
        NORM: "Golongan Karya"},
    {
        ORTH: "GOR",
        LEMMA: "Gelanggang Olah Raga",
        NORM: "Gelanggang Olah Raga"},
    {
        ORTH: "HAM",
        LEMMA: "hak asasi manusia",
        NORM: "hak asasi manusia"},
    {
        ORTH: "hansip",
        LEMMA: "pertahanan sipil",
        NORM: "pertahanan sipil"},
    {
        ORTH: "Hanura",
        LEMMA: "hati nurani rakyat",
        NORM: "hati nurani rakyat"},
    {
        ORTH: "Hardiknas",
        LEMMA: "Hari Pendidikan Nasional",
        NORM: "Hari Pendidikan Nasional"},
    {
        ORTH: "Harkitnas",
        LEMMA: "Hari Kebangkitan Nasional",
        NORM: "Hari Kebangkitan Nasional"},
    {
        ORTH: "Harbolnas",
        LEMMA: "Hari Belanja Online Nasional",
        NORM: "Hari Belanja Online Nasional"},
    {
        ORTH: "HGB",
        LEMMA: "hak guna bangunan",
        NORM: "hak guna bangunan"},
    {
        ORTH: "HGU",
        LEMMA: "hak guna usaha",
        NORM: "hak guna usaha"},
    {
        ORTH: "humas",
        LEMMA: "hubungan masyarakat",
        NORM: "hubungan masyarakat"},
    {
        ORTH: "HUT",
        LEMMA: "hari ulang tahun",
        NORM: "hari ulang tahun"},
    {
        ORTH: "IDI",
        LEMMA: "Ikatan Dokter Indonesia",
        NORM: "Ikatan Dokter Indonesia"},
    {
        ORTH: "IGD",
        LEMMA: "Instalasi Gawat Darurat",
        NORM: "Instalasi Gawat Darurat"},
    {
        ORTH: "info",
        LEMMA: "informasi",
        NORM: "informasi"},
    {
        ORTH: "IPA",
        LEMMA: "ilmu pengetahuan alam",
        NORM: "ilmu pengetahuan alam"},
    {
        ORTH: "IPB",
        LEMMA: "Institut Pertanian Bogor",
        NORM: "Institut Pertanian Bogor"},
    {
        ORTH: "IPS",
        LEMMA: "ilmu pengetahuan sosial",
        NORM: "ilmu pengetahuan sosial"},
    {
        ORTH: "irjen",
        LEMMA: "inspektur jenderal",
        NORM: "inspektur jenderal"},
    {
        ORTH: "Irjen",
        LEMMA: "inspektur jenderal",
        NORM: "inspektur jenderal"},
    {
        ORTH: "irjenpol",
        LEMMA: "inspektur jenderal polisi",
        NORM: "inspektur jenderal polisi"},
    {
        ORTH: "Irjenpol",
        LEMMA: "inspektur jenderal polisi",
        NORM: "inspektur jenderal polisi"},
    {
        ORTH: "ITB",
        LEMMA: "Institut Teknologi Bandung",
        NORM: "Institut Teknologi Bandung"},
    {
        ORTH: "ITS",
        LEMMA: "Institut Teknologi Sepuluh November",
        NORM: "Institut Teknologi Sepuluh November"},
    {
        ORTH: "jabar",
        LEMMA: "Jawa Barat",
        NORM: "Jawa Barat"},
    {
        ORTH: "Jabar",
        LEMMA: "Jawa Barat",
        NORM: "Jawa Barat"},
    {
        ORTH: "jabodetabek",
        LEMMA: "Jakarta Bogor Depok Tangerang Bekasi",
        NORM: "Jakarta Bogor Depok Tangerang Bekasi"},
    {
        ORTH: "Jabodetabek",
        LEMMA: "Jakarta Bogor Depok Tangerang Bekasi",
        NORM: "Jakarta Bogor Depok Tangerang Bekasi"},
    {
        ORTH: "jabotabek",
        LEMMA: "Jakarta Bogor Tangerang Bekasi",
        NORM: "Jakarta Bogor Tangerang Bekasi"},
    {
        ORTH: "Jabotabek",
        LEMMA: "Jakarta Bogor Tangerang Bekasi",
        NORM: "Jakarta Bogor Tangerang Bekasi"},
    {
        ORTH: "Jakbar",
        LEMMA: "Jakarta Barat",
        NORM: "Jakarta Barat"},
    {
        ORTH: "Jakgung",
        LEMMA: "Jaksa Agung",
        NORM: "Jaksa Agung"},
    {
        ORTH: "Jakpus",
        LEMMA: "Jakarta Pusat",
        NORM: "Jakarta Pusat"},
    {
        ORTH: "Jaksel",
        LEMMA: "Jakarta Selatan",
        NORM: "Jakarta Selatan"},
    {
        ORTH: "Jaktim",
        LEMMA: "Jakarta Timur",
        NORM: "Jakarta Timur"},
    {
        ORTH: "Jakut",
        LEMMA: "Jakarta Utara",
        NORM: "Jakarta Utara"},
    {
        ORTH: "Jamsostek",
        LEMMA: "Jaminan Sosial Tenaga Kerja",
        NORM: "Jaminan Sosial Tenaga Kerja"},
    {
        ORTH: "Jateng",
        LEMMA: "Jawa Tengah",
        NORM: "Jawa Tengah"},
    {
        ORTH: "Jatim",
        LEMMA: "Jawa Timur",
        NORM: "Jawa Timur"},
    {
        ORTH: "kadispen",
        LEMMA: "kepala dinas penerangan",
        NORM: "kepala dinas penerangan"},
    {
        ORTH: "Kalbar",
        LEMMA: "Kalimantan Barat",
        NORM: "Kalimantan Barat"},
    {
        ORTH: "Kalsel",
        LEMMA: "Kalimantan Selatan",
        NORM: "Kalimantan Selatan"},
    {
        ORTH: "Kalteng",
        LEMMA: "Kalimantan Tengah",
        NORM: "Kalimantan Tengah"},
    {
        ORTH: "Kaltim",
        LEMMA: "Kalimantan Timur",
        NORM: "Kalimantan Timur"},
    {
        ORTH: "kanwil",
        LEMMA: "kantor wilayah",
        NORM: "kantor wilayah"},
    {
        ORTH: "kapol",
        LEMMA: "kepala polisi",
        NORM: "kepala polisi"},
    {
        ORTH: "Kapolda",
        LEMMA: "Kepala Kepolisian Daerah",
        NORM: "Kepala Kepolisian Daerah"},
    {
        ORTH: "Kapolres",
        LEMMA: "Kepala Kepolisian Resor",
        NORM: "Kepala Kepolisian Resor"},
    {
        ORTH: "Kapolresta",
        LEMMA: "Kepala Kepolisian Resor Kota",
        NORM: "Kepala Kepolisian Resor Kota"},
    {
        ORTH: "Kapolri",
        LEMMA: "Kepala Kepolisian Republik Indonesia",
        NORM: "Kepala Kepolisian Republik Indonesia"},
    {
        ORTH: "Kapolsek",
        LEMMA: "Kepala Kepolisian Sektor",
        NORM: "Kepala Kepolisian Sektor"},
    {
        ORTH: "Kapoltabes",
        LEMMA: "Kepala Kepolisian Kota Besar",
        NORM: "Kepala Kepolisian Kota Besar"},
    {
        ORTH: "Kapolwil",
        LEMMA: "kepala kepolisian wilayah",
        NORM: "kepala kepolisian wilayah"},
    {
        ORTH: "kapt.",
        LEMMA: "kapten",
        NORM: "kapten"},
    {
        ORTH: "kedubes",
        LEMMA: "kedutaan besar",
        NORM: "kedutaan besar"},
    {
        ORTH: "Kejagung",
        LEMMA: "Kejaksaan Agung",
        NORM: "Kejaksaan Agung"},
    {
        ORTH: "keppres",
        LEMMA: "Keputusan Presiden",
        NORM: "Keputusan Presiden"},
    {
        ORTH: "KJRI",
        LEMMA: "Konsulat Jenderal Republik Indonesia",
        NORM: "Konsulat Jenderal Republik Indonesia"},
    {
        ORTH: "kodam",
        LEMMA: "komando daerah militer",
        NORM: "komando daerah militer"},
    {
        ORTH: "kodim",
        LEMMA: "komando distrik militer",
        NORM: "komando distrik militer"},
    {
        ORTH: "kombes",
        LEMMA: "komisaris besar",
        NORM: "komisaris besar"},
    {
        ORTH: "komjenpol",
        LEMMA: "komisaris jenderal polisi",
        NORM: "komisaris jenderal polisi"},
    {
        ORTH: "komnas",
        LEMMA: "komisi nasional",
        NORM: "komisi nasional"},
    {
        ORTH: "KONI",
        LEMMA: "Komite Olahraga Nasional Indonesia",
        NORM: "Komite Olahraga Nasional Indonesia"},
    {
        ORTH: "konjen",
        LEMMA: "konsulat jenderal",
        NORM: "konsulat jenderal"},
    {
        ORTH: "Kopaja",
        LEMMA: "Koperasi Angkutan Jakarta",
        NORM: "Koperasi Angkutan Jakarta"},
    {
        ORTH: "kopaska",
        LEMMA: "komando pasukan katak",
        NORM: "komando pasukan katak"},
    {
        ORTH: "kopassus",
        LEMMA: "komando pasukan khusus",
        NORM: "komando pasukan khusus"},
    {
        ORTH: "KOPASSUS",
        LEMMA: "Komando Pasukan Khusus",
        NORM: "Komando Pasukan Khusus"},
    {
        ORTH: "kopda",
        LEMMA: "kopral dua",
        NORM: "kopral dua"},
    {
        ORTH: "Kopertis",
        LEMMA: "Koordinasi Perguruan Tinggi Swasta",
        NORM: "Koordinasi Perguruan Tinggi Swasta"},
    {
        ORTH: "Koramil",
        LEMMA: "Komando Rayon Militer",
        NORM: "Komando Rayon Militer"},
    {
        ORTH: "Korem",
        LEMMA: "Komando Resor Militer",
        NORM: "Komando Resor Militer"},
    {
        ORTH: "Korsel",
        LEMMA: "Korea Selatan",
        NORM: "Korea Selatan"},
    {
        ORTH: "Korut",
        LEMMA: "Korea Utara",
        NORM: "Korea Utara"},
    {
        ORTH: "Kostrad",
        LEMMA: "Komando Cadangan Strategis Angkatan Darat",
        NORM: "Komando Cadangan Strategis Angkatan Darat"},
    {
        ORTH: "KPK",
        LEMMA: "Komisi Pemberantasan Korupsi",
        NORM: "Komisi Pemberantasan Korupsi"},
    {
        ORTH: "KPPN",
        LEMMA: "Kantor Pusat Perbendaharaan Negara",
        NORM: "Kantor Pusat Perbendaharaan Negara"},
    {
        ORTH: "KPPU",
        LEMMA: "Komisi Pengawas Persaingan Usaha",
        NORM: "Komisi Pengawas Persaingan Usaha"},
    {
        ORTH: "KPR",
        LEMMA: "kredit pemilikan rumah",
        NORM: "kredit pemilikan rumah"},
    {
        ORTH: "KPU",
        LEMMA: "Komisi Pemilihan Umum",
        NORM: "Komisi Pemilihan Umum"},
    {
        ORTH: "KPUD",
        LEMMA: "Komisi Pemilihan Umum Daerah",
        NORM: "Komisi Pemilihan Umum Daerah"},
    {
        ORTH: "KRL",
        LEMMA: "kereta rel listrik",
        NORM: "kereta rel listrik"},
    {
        ORTH: "KSAB",
        LEMMA: "Kepala Staf Angkatan Bersenjata",
        NORM: "Kepala Staf Angkatan Bersenjata"},
    {
        ORTH: "KSAD",
        LEMMA: "Kepala Staf Angkatan Darat",
        NORM: "Kepala Staf Angkatan Darat"},
    {
        ORTH: "KSAL",
        LEMMA: "Kepala Staf Angkatan Laut",
        NORM: "Kepala Staf Angkatan Laut"},
    {
        ORTH: "KSAU",
        LEMMA: "Kepala Staf Angkatan Udara",
        NORM: "Kepala Staf Angkatan Udara"},
    {
        ORTH: "KUHAP",
        LEMMA: "kitab undang-undang hukum acara pidana",
        NORM: "kitab undang-undang hukum acara pidana"},
    {
        ORTH: "KUHP",
        LEMMA: "kitab undang-undang hukum pidana",
        NORM: "kitab undang-undang hukum pidana"},
    {
        ORTH: "KUHPT",
        LEMMA: "kitab undang-undang hukum pidana tentara",
        NORM: "kitab undang-undang hukum pidana tentara"},
    {
        ORTH: "LAPAN",
        LEMMA: "Lembaga Penerbangan dan Antariksa Nasional",
        NORM: "Lembaga Penerbangan dan Antariksa Nasional"},
    {
        ORTH: "lapas",
        LEMMA: "lembaga pemasyarakatan",
        NORM: "lembaga pemasyarakatan"},
    {
        ORTH: "Lapas",
        LEMMA: "lembaga pemasyarakatan",
        NORM: "lembaga pemasyarakatan"},
    {
        ORTH: "LBH",
        LEMMA: "lembaga bantuan hukum",
        NORM: "lembaga bantuan hukum"},
    {
        ORTH: "letda",
        LEMMA: "letnan dua",
        NORM: "letnan dua"},
    {
        ORTH: "Letda",
        LEMMA: "letnan dua",
        NORM: "letnan dua"},
    {
        ORTH: "letjen",
        LEMMA: "letnan jenderal",
        NORM: "letnan jenderal"},
    {
        ORTH: "Letjen",
        LEMMA: "letnan jenderal",
        NORM: "letnan jenderal"},
    {
        ORTH: "lettu",
        LEMMA: "letnan satu",
        NORM: "letnan satu"},
    {
        ORTH: "LIPI",
        LEMMA: "Lembaga Ilmu Pengetahuan Indonesia",
        NORM: "Lembaga Ilmu Pengetahuan Indonesia"},
    {
        ORTH: "litbang",
        LEMMA: "penelitian dan pengembangan",
        NORM: "penelitian dan pengembangan"},
    {
        ORTH: "LSI",
        LEMMA: "Lembaga Survei Indonesia",
        NORM: "Lembaga Survei Indonesia"},
    {
        ORTH: "LSM",
        LEMMA: "Lembaga Swadaya Masyarakat",
        NORM: "Lembaga Swadaya Masyarakat"},
    {
        ORTH: "mabes",
        LEMMA: "markas besar",
        NORM: "markas besar"},
    {
        ORTH: "Menag",
        LEMMA: "Menteri Agama",
        NORM: "Menteri Agama"},
    {
        ORTH: "Menaker",
        LEMMA: "Menteri Tenaga Kerja",
        NORM: "Menteri Tenaga Kerja"},
    {
        ORTH: "Menakertrans",
        LEMMA: "Menteri Tenaga Kerja dan Transmigrasi",
        NORM: "Menteri Tenaga Kerja dan Transmigrasi"},
    {
        ORTH: "Menbudpar",
        LEMMA: "Menteri Kebudayaan dan Pariwisata",
        NORM: "Menteri Kebudayaan dan Pariwisata"},
    {
        ORTH: "Mendagri",
        LEMMA: "Menteri Dalam Negeri",
        NORM: "Menteri Dalam Negeri"},
    {
        ORTH: "Mendikbud",
        LEMMA: "Menteri Pendidikan dan Kebudayaan",
        NORM: "Menteri Pendidikan dan Kebudayaan"},
    {
        ORTH: "Mendiknas",
        LEMMA: "Menteri Pendidikan Nasional",
        NORM: "Menteri Pendidikan Nasional"},
    {
        ORTH: "Menhan",
        LEMMA: "Menteri Pertahanan",
        NORM: "Menteri Pertahanan"},
    {
        ORTH: "Menkes",
        LEMMA: "Menteri Kesehatan",
        NORM: "Menteri Kesehatan"},
    {
        ORTH: "Menkeu",
        LEMMA: "Menteri Keuangan",
        NORM: "Menteri Keuangan"},
    {
        ORTH: "Menko",
        LEMMA: "Menteri Koordinator",
        NORM: "Menteri Koordinator"},
    {
        ORTH: "Menkominfo",
        LEMMA: "Menteri Komunikasi dan Informatika",
        NORM: "Menteri Komunikasi dan Informatika"},
    {
        ORTH: "Menkumdang",
        LEMMA: "Menteri Hukum dan Perundang-undangan",
        NORM: "Menteri Hukum dan Perundang-undangan"},
    {
        ORTH: "Menlu",
        LEMMA: "Menteri Luar Negeri",
        NORM: "Menteri Luar Negeri"},
    {
        ORTH: "Menpora",
        LEMMA: "Menteri Pemuda dan Olahraga",
        NORM: "Menteri Pemuda dan Olahraga"},
    {
        ORTH: "Menristek",
        LEMMA: "Menteri Negara Riset dan Teknologi",
        NORM: "Menteri Negara Riset dan Teknologi"},
    {
        ORTH: "Mensesneg",
        LEMMA: "Menteri Sekretaris Negara",
        NORM: "Menteri Sekretaris Negara"},
    {
        ORTH: "Mensos",
        LEMMA: "Menteri Sosial",
        NORM: "Menteri Sosial"},
    {
        ORTH: "MPR",
        LEMMA: "Majelis Permusyawaratan Rakyat",
        NORM: "Majelis Permusyawaratan Rakyat"},
    {
        ORTH: "MUI",
        LEMMA: "Majelis Ulama Indonesia",
        NORM: "Majelis Ulama Indonesia"},
    {
        ORTH: "NTB",
        LEMMA: "Nusa Tenggara Barat",
        NORM: "Nusa Tenggara Barat"},
    {
        ORTH: "NTT",
        LEMMA: "Nusa Tenggara Timur",
        NORM: "Nusa Tenggara Timur"},
    {
        ORTH: "NU",
        LEMMA: "Nahdatul Ulama",
        NORM: "Nahdatul Ulama"},
    {
        ORTH: "OJK",
        LEMMA: "Otoritas Jasa Keuangan",
        NORM: "Otoritas Jasa Keuangan"},
    {
        ORTH: "OKU",
        LEMMA: "Ogan Komering Ulu",
        NORM: "Ogan Komering Ulu"},
    {
        ORTH: "ormas",
        LEMMA: "organisasi massa",
        NORM: "organisasi massa"},
    {
        ORTH: "PADI",
        LEMMA: "Partai Aliansi Demokrat Indonesia",
        NORM: "Partai Aliansi Demokrat Indonesia"},
    {
        ORTH: "PAM",
        LEMMA: "perusahaan air minum",
        NORM: "perusahaan air minum"},
    {
        ORTH: "PAN",
        LEMMA: "Partai Amanat Nasional",
        NORM: "Partai Amanat Nasional"},
    {
        ORTH: "Panwaslu",
        LEMMA: "Panitia Pengawas Pemilihan Umum",
        NORM: "Panitia Pengawas Pemilihan Umum"},
    {
        ORTH: "parpol",
        LEMMA: "partai politik",
        NORM: "partai politik"},
    {
        ORTH: "PATI",
        LEMMA: "Perhimpunan Ahli Teknik Indonesia",
        NORM: "Perhimpunan Ahli Teknik Indonesia"},
    {
        ORTH: "PDI",
        LEMMA: "Partai Demokrasi Indonesia",
        NORM: "Partai Demokrasi Indonesia"},
    {
        ORTH: "PDIP",
        LEMMA: "Partai Demokrasi Indonesia Perjuangan",
        NORM: "Partai Demokrasi Indonesia Perjuangan"},
    {
        ORTH: "pelatda",
        LEMMA: "pemusatan latihan daerah",
        NORM: "pemusatan latihan daerah"},
    {
        ORTH: "pelatnas",
        LEMMA: "pemusatan latihan nasional",
        NORM: "pemusatan latihan nasional"},
    {
        ORTH: "Pelni",
        LEMMA: "Pelayanan Nasional Indonesia",
        NORM: "Pelayanan Nasional Indonesia"},
    {
        ORTH: "pemda",
        LEMMA: "pemerintah daerah",
        NORM: "pemerintah daerah"},
    {
        ORTH: "pemilu",
        LEMMA: "pemilihan umum",
        NORM: "pemilihan umum"},
    {
        ORTH: "pemkot",
        LEMMA: "pemerintah kota",
        NORM: "pemerintah kota"},
    {
        ORTH: "pemprov",
        LEMMA: "pemerintah provinsi",
        NORM: "pemerintah provinsi"},
    {
        ORTH: "penjas",
        LEMMA: "pendidikan jasmani",
        NORM: "pendidikan jasmani"},
    {
        ORTH: "Perbakin",
        LEMMA: "Persatuan Penembak Indonesia",
        NORM: "Persatuan Penembak Indonesia"},
    {
        ORTH: "Perbanas",
        LEMMA: "Perhimpunan Bank Swasta Nasional",
        NORM: "Perhimpunan Bank Swasta Nasional"},
    {
        ORTH: "perda",
        LEMMA: "peraturan daerah",
        NORM: "peraturan daerah"},
    {
        ORTH: "perpres",
        LEMMA: "peraturan presiden",
        NORM: "peraturan presiden"},
    {
        ORTH: "Perpres",
        LEMMA: "peraturan presiden",
        NORM: "peraturan presiden"},
    {
        ORTH: "PERPRES",
        LEMMA: "peraturan presiden",
        NORM: "peraturan presiden"},
    {
        ORTH: "PKS",
        LEMMA: "Partai Keadilan Sejahtera",
        NORM: "Partai Keadilan Sejahtera"},
    {
        ORTH: "PLN",
        LEMMA: "Perusahaan Listrik Negara",
        NORM: "Perusahaan Listrik Negara"},
    {
        ORTH: "PLTA",
        LEMMA: "Pembangkit Listrik Tenaga Air",
        NORM: "Pembangkit Listrik Tenaga Air"},
    {
        ORTH: "PLTD",
        LEMMA: "Pembangkit Listrik Tenaga Diesel",
        NORM: "Pembangkit Listrik Tenaga Diesel"},
    {
        ORTH: "PLTG",
        LEMMA: "pusat listrik tenaga gas",
        NORM: "pusat listrik tenaga gas"},
    {
        ORTH: "PLTN",
        LEMMA: "Pembangkit Listrik Tenaga Nuklir",
        NORM: "Pembangkit Listrik Tenaga Nuklir"},
    {
        ORTH: "PLTU",
        LEMMA: "Pembangkit Listrik Tenaga Uap",
        NORM: "Pembangkit Listrik Tenaga Uap"},
    {
        ORTH: "PMDK",
        LEMMA: "penelusuran minat dan kemampuan",
        NORM: "penelusuran minat dan kemampuan"},
    {
        ORTH: "PMI",
        LEMMA: "Palang Merah Indonesia",
        NORM: "Palang Merah Indonesia"},
    {
        ORTH: "PNS",
        LEMMA: "Pegawai Negeri Sipil",
        NORM: "Pegawai Negeri Sipil"},
    {
        ORTH: "polantas",
        LEMMA: "polisi lalu lintas",
        NORM: "polisi lalu lintas"},
    {
        ORTH: "Polantas",
        LEMMA: "polisi lalu lintas",
        NORM: "polisi lalu lintas"},
    {
        ORTH: "polda",
        LEMMA: "kepolisian daerah",
        NORM: "kepolisian daerah"},
    {
        ORTH: "Polda",
        LEMMA: "kepolisian daerah",
        NORM: "kepolisian daerah"},
    {
        ORTH: "Polhukam",
        LEMMA: "Politik, Hukum dan Keamanan",
        NORM: "Politik, Hukum dan Keamanan"},
    {
        ORTH: "polres",
        LEMMA: "polisi resor",
        NORM: "polisi resor"},
    {
        ORTH: "Polres",
        LEMMA: "kepolisian resor",
        NORM: "kepolisian resor"},
    {
        ORTH: "polri",
        LEMMA: "kepolisian Republik Indonesia",
        NORM: "kepolisian Republik Indonesia"},
    {
        ORTH: "Polri",
        LEMMA: "kepolisian Republik Indonesia",
        NORM: "kepolisian Republik Indonesia"},
    {
        ORTH: "POLRI",
        LEMMA: "kepolisian Republik Indonesia",
        NORM: "kepolisian Republik Indonesia"},
    {
        ORTH: "polsek",
        LEMMA: "kepolisian sektor",
        NORM: "kepolisian sektor"},
    {
        ORTH: "polwan",
        LEMMA: "polisi wanita",
        NORM: "polisi wanita"},
    {
        ORTH: "Polwan",
        LEMMA: "polisi wanita",
        NORM: "polisi wanita"},
    {
        ORTH: "PON",
        LEMMA: "Pekan Olahraga Nasional",
        NORM: "Pekan Olahraga Nasional"},
    {
        ORTH: "Poskamling",
        LEMMA: "Pos Keamanan Lingkungan",
        NORM: "Pos Keamanan Lingkungan"},
    {
        ORTH: "Posko",
        LEMMA: "Pos Komando",
        NORM: "Pos Komando"},
    {
        ORTH: "Posyandu",
        LEMMA: "Pos Pelayanan Terpadu",
        NORM: "Pos Pelayanan Terpadu"},
    {
        ORTH: "PPN",
        LEMMA: "Pajak Pertambahan Nilai",
        NORM: "Pajak Pertambahan Nilai"},
    {
        ORTH: "PPPK",
        LEMMA: "pertolongan pertama pada kecelakaan",
        NORM: "pertolongan pertama pada kecelakaan"},
    {
        ORTH: "P3K",
        LEMMA: "pertolongan pertama pada kecelakaan",
        NORM: "pertolongan pertama pada kecelakaan"},
    {
        ORTH: "PTN",
        LEMMA: "perguruan tinggi negeri",
        NORM: "perguruan tinggi negeri"},
    {
        ORTH: "PTS",
        LEMMA: "perguruan tinggi swasta",
        NORM: "perguruan tinggi swasta"},
    {
        ORTH: "pungli",
        LEMMA: "pungutan liar",
        NORM: "pungutan liar"},
    {
        ORTH: "puskesmas",
        LEMMA: "pusat kesehatan masyarakat",
        NORM: "pusat kesehatan masyarakat"},
    {
        ORTH: "Puskesmas",
        LEMMA: "pusat kesehatan masyarakat",
        NORM: "pusat kesehatan masyarakat"},
    {
        ORTH: "puslitbang",
        LEMMA: "Pusat Penelitian dan Pengembangan",
        NORM: "Pusat Penelitian dan Pengembangan"},
    {
        ORTH: "Puslitbang",
        LEMMA: "Pusat Penelitian dan Pengembangan",
        NORM: "Pusat Penelitian dan Pengembangan"},
    {
        ORTH: "raker",
        LEMMA: "rapat kerja",
        NORM: "rapat kerja"},
    {
        ORTH: "rakernas",
        LEMMA: "rapat kerja nasional",
        NORM: "rapat kerja nasional"},
    {
        ORTH: "rakor",
        LEMMA: "rapat koordinasi",
        NORM: "rapat koordinasi"},
    {
        ORTH: "ranmor",
        LEMMA: "kendaraan bermotor",
        NORM: "kendaraan bermotor"},
    {
        ORTH: "RAPBD",
        LEMMA: "Rancangan Anggaran Pendapatan dan Belanja Daerah",
        NORM: "Rancangan Anggaran Pendapatan dan Belanja Daerah"},
    {
        ORTH: "RAPBN",
        LEMMA: "Rancangan Anggaran Pendapatan dan Belanja Negara",
        NORM: "Rancangan Anggaran Pendapatan dan Belanja Negara"},
    {
        ORTH: "rapim",
        LEMMA: "rapat pimpinan",
        NORM: "rapat pimpinan"},
    {
        ORTH: "resko",
        LEMMA: "resor kota",
        NORM: "resor kota"},
    {
        ORTH: "reskrim",
        LEMMA: "reserse kriminal",
        NORM: "reserse kriminal"},
    {
        ORTH: "resmob",
        LEMMA: "reserse mobil",
        NORM: "reserse mobil"},
    {
        ORTH: "restik",
        LEMMA: "reserse narkotika",
        NORM: "reserse narkotika"},
    {
        ORTH: "RI",
        LEMMA: "Republik Indonesia",
        NORM: "Republik Indonesia"},
    {
        ORTH: "RSAD",
        LEMMA: "Rumah Sakit Angkatan Darat",
        NORM: "Rumah Sakit Angkatan Darat"},
    {
        ORTH: "RSAL",
        LEMMA: "Rumah Sakit Angkatan Laut",
        NORM: "Rumah Sakit Angkatan Laut"},
    {
        ORTH: "RSB",
        LEMMA: "Rumah Sakit Bersalin",
        NORM: "Rumah Sakit Bersalin"},
    {
        ORTH: "RSIA",
        LEMMA: "Rumah Sakit Ibu dan Anak",
        NORM: "Rumah Sakit Ibu dan Anak"},
    {
        ORTH: "RSJ",
        LEMMA: "Rumah Sakit Jiwa",
        NORM: "Rumah Sakit Jiwa"},
    {
        ORTH: "RSPAD",
        LEMMA: "Rumah Sakit Pusat Angkatan Darat",
        NORM: "Rumah Sakit Pusat Angkatan Darat"},
    {
        ORTH: "RSU",
        LEMMA: "Rumah Sakit Umum",
        NORM: "Rumah Sakit Umum"},
    {
        ORTH: "RSUD",
        LEMMA: "Rumah Sakit Umum Daerah",
        NORM: "Rumah Sakit Umum Daerah"},
    {
        ORTH: "RSUP",
        LEMMA: "Rumah Sakit Umum Pusat",
        NORM: "Rumah Sakit Umum Pusat"},
    {
        ORTH: "RT",
        LEMMA: "rukun tetangga",
        NORM: "rukun tetangga"},
    {
        ORTH: "RW",
        LEMMA: "rukun warga",
        NORM: "rukun warga"},
    {
        ORTH: "rusun",
        LEMMA: "rumah susun",
        NORM: "rumah susun"},
    {
        ORTH: "rusunawa",
        LEMMA: "Rumah Susun Sederhana Sewa",
        NORM: "Rumah Susun Sederhana Sewa"},
    {
        ORTH: "rusunami",
        LEMMA: "Rumah Susun Sederhana Milik",
        NORM: "Rumah Susun Sederhana Milik"},
    {
        ORTH: "rutan",
        LEMMA: "rumah tahanan",
        NORM: "rumah tahanan"},
    {
        ORTH: "RUU",
        LEMMA: "rancangan undang-undang",
        NORM: "rancangan undang-undang"},
    {
        ORTH: "RUUD",
        LEMMA: "rancangan undang-undang darurat",
        NORM: "rancangan undang-undang darurat"},
    {
        ORTH: "samsat",
        LEMMA: "sistem administrasi manunggal satu atap",
        NORM: "sistem administrasi manunggal satu atap"},
    {
        ORTH: "Samsat",
        LEMMA: "sistem administrasi manunggal satu atap",
        NORM: "sistem administrasi manunggal satu atap"},
    {
        ORTH: "SAR",
        LEMMA: "Search and Rescue",
        NORM: "Search and Rescue"},
    {
        ORTH: "sara",
        LEMMA: "suku, agama, ras, dan antargolongan",
        NORM: "suku, agama, ras, dan antargolongan"},
    {
        ORTH: "SARA",
        LEMMA: "suku, agama, ras, dan antargolongan",
        NORM: "suku, agama, ras, dan antargolongan"},
    {
        ORTH: "satgas",
        LEMMA: "satuan tugas",
        NORM: "satuan tugas"},
    {
        ORTH: "satker",
        LEMMA: "satuan kerja",
        NORM: "satuan kerja"},
    {
        ORTH: "satpam",
        LEMMA: "satuan pengamanan",
        NORM: "satuan pengamanan"},
    {
        ORTH: "satpolantas",
        LEMMA: "kesatuan polisi lalu lintas",
        NORM: "kesatuan polisi lalu lintas"},
    {
        ORTH: "SD",
        LEMMA: "Sekolah Dasar",
        NORM: "Sekolah Dasar"},
    {
        ORTH: "SDM",
        LEMMA: "sumber daya manusia",
        NORM: "sumber daya manusia"},
    {
        ORTH: "SDN",
        LEMMA: "Sekolah Dasar Negeri",
        NORM: "Sekolah Dasar Negeri"},
    {
        ORTH: "sekda",
        LEMMA: "sekretaris daerah",
        NORM: "sekretaris daerah"},
    {
        ORTH: "Sekda",
        LEMMA: "sekretaris daerah",
        NORM: "sekretaris daerah"},
    {
        ORTH: "sekjen",
        LEMMA: "sekretaris jenderal",
        NORM: "sekretaris jenderal"},
    {
        ORTH: "Sekjen",
        LEMMA: "sekretaris jenderal",
        NORM: "sekretaris jenderal"},
    {
        ORTH: "sembako",
        LEMMA: "sembilan bahan pokok",
        NORM: "sembilan bahan pokok"},
    {
        ORTH: "Sesneg",
        LEMMA: "Sekretaris Negara",
        NORM: "Sekretaris Negara"},
    {
        ORTH: "setjen",
        LEMMA: "sekretariat jenderal",
        NORM: "sekretariat jenderal"},
    {
        ORTH: "setneg",
        LEMMA: "Sekretariat Negara",
        NORM: "Sekretariat Negara"},
    {
        ORTH: "SLB",
        LEMMA: "sekolah luar biasa",
        NORM: "sekolah luar biasa"},
    {
        ORTH: "SMA",
        LEMMA: "Sekolah Menengah Atas",
        NORM: "Sekolah Menengah Atas"},
    {
        ORTH: "SMAN",
        LEMMA: "Sekolah Menengah Atas Negeri",
        NORM: "Sekolah Menengah Atas Negeri"},
    {
        ORTH: "SMP",
        LEMMA: "Sekolah Menengah Pertama",
        NORM: "Sekolah Menengah Pertama"},
    {
        ORTH: "SMPN",
        LEMMA: "Sekolah Menengah Pertama Negeri",
        NORM: "Sekolah Menengah Pertama Negeri"},
    {
        ORTH: "SPPT",
        LEMMA: "Surat Pemberitahuan Pajak Terhutang",
        NORM: "Surat Pemberitahuan Pajak Terhutang"},
    {
        ORTH: "STNK",
        LEMMA: "Surat Tanda Nomor Kendaraan",
        NORM: "Surat Tanda Nomor Kendaraan"},
    {
        ORTH: "Sulbar",
        LEMMA: "Sulawesi Barat",
        NORM: "Sulawesi Barat"},
    {
        ORTH: "Sulsel",
        LEMMA: "Sulawesi Selatan",
        NORM: "Sulawesi Selatan"},
    {
        ORTH: "Sulteng",
        LEMMA: "Sulawesi Tengah",
        NORM: "Sulawesi Tengah"},
    {
        ORTH: "Sultra",
        LEMMA: "Sulawesi Tenggara",
        NORM: "Sulawesi Tenggara"},
    {
        ORTH: "Sulut",
        LEMMA: "Sulawesi Utara",
        NORM: "Sulawesi Utara"},
    {
        ORTH: "Sumbar",
        LEMMA: "Sumatera Barat",
        NORM: "Sumatera Barat"},
    {
        ORTH: "Sumsel",
        LEMMA: "Sumatera Selatan",
        NORM: "Sumatera Selatan"},
    {
        ORTH: "Sumteng",
        LEMMA: "Sumatera Tengah",
        NORM: "Sumatera Tengah"},
    {
        ORTH: "Sumtim",
        LEMMA: "Sumatera Timur",
        NORM: "Sumatera Timur"},
    {
        ORTH: "Sumut",
        LEMMA: "Sumatera Utara",
        NORM: "Sumatera Utara"},
    {
        ORTH: "Supersemar",
        LEMMA: "Surat Perintah Sebelas Maret",
        NORM: "Surat Perintah Sebelas Maret"},
    {
        ORTH: "TKI",
        LEMMA: "Tenaga Kerja Indonesia",
        NORM: "Tenaga Kerja Indonesia"},
    {
        ORTH: "TKW",
        LEMMA: "Tenaga Kerja Wanita",
        NORM: "Tenaga Kerja Wanita"},
    {
        ORTH: "TNI",
        LEMMA: "Tentara Nasional Indonesia",
        NORM: "Tentara Nasional Indonesia"},
    {
        ORTH: "TPS",
        LEMMA: "tempat pemungutan suara",
        NORM: "tempat pemungutan suara"},
    {
        ORTH: "Trikora",
        LEMMA: "trikomando rakyat",
        NORM: "trikomando rakyat"},
    {
        ORTH: "tritura",
        LEMMA: "tri tuntutan rakyat",
        NORM: "tri tuntutan rakyat"},
    {
        ORTH: "UGD",
        LEMMA: "Unit Gawat Darurat",
        NORM: "Unit Gawat Darurat"},
    {
        ORTH: "UKM",
        LEMMA: "Usaha Kecil dan Menengah",
        NORM: "Usaha Kecil dan Menengah"},
    {
        ORTH: "ultah",
        LEMMA: "ulang tahun",
        NORM: "ulang tahun"},
    {
        ORTH: "UMP",
        LEMMA: "upah minimum provinsi",
        NORM: "upah minimum provinsi"},
    {
        ORTH: "UMPTN",
        LEMMA: "ujian masuk perguruan tinggi negeri",
        NORM: "ujian masuk perguruan tinggi negeri"},
    {
        ORTH: "UMR",
        LEMMA: "upah minimum regional",
        NORM: "upah minimum regional"},
    {
        ORTH: "UUD",
        LEMMA: "Undang-Undang Dasar",
        NORM: "Undang-Undang Dasar"},
    {
        ORTH: "UGM",
        LEMMA: "Universitas Gadjah Mada",
        NORM: "Universitas Gadjah Mada"},
    {
        ORTH: "UI",
        LEMMA: "Universitas Indonesia",
        NORM: "Universitas Indonesia"},
    {
        ORTH: "UIN",
        LEMMA: "Universitas Islam Negeri",
        NORM: "Universitas Islam Negeri"},
    {
        ORTH: "UKRIDA",
        LEMMA: "Universitas Kristen Krida Wacana",
        NORM: "Universitas Kristen Krida Wacana"},
    {
        ORTH: "Unair",
        LEMMA: "Universitas Airlangga",
        NORM: "Universitas Airlangga"},
    {
        ORTH: "Unpad",
        LEMMA: "Universitas Padjadjaran",
        NORM: "Universitas Padjadjaran"},
    {
        ORTH: "UMB",
        LEMMA: "Universitas Mercu Buana",
        NORM: "Universitas Mercu Buana"},
    {
        ORTH: "VUTW",
        LEMMA: "Varietas Unggul Tahan Wereng",
        NORM: "Varietas Unggul Tahan Wereng"},
    {
        ORTH: "wagub",
        LEMMA: "wakil gubernur",
        NORM: "wakil gubernur"},
    {
        ORTH: "wapres",
        LEMMA: "Wakil Presiden",
        NORM: "Wakil Presiden"},
    {
        ORTH: "warnet",
        LEMMA: "warung internet",
        NORM: "warung internet"},
    {
        ORTH: "warteg",
        LEMMA: "warung tegal",
        NORM: "warung tegal"},
    {
        ORTH: "wartel",
        LEMMA: "warung telekomunikasi",
        NORM: "warung telekomunikasi"},
    {
        ORTH: "waserda",
        LEMMA: "warung serba ada",
        NORM: "warung serba ada"},
    {
        ORTH: "WIB",
        LEMMA: "Waktu Indonesia Barat",
        NORM: "Waktu Indonesia Barat"},
    {
        ORTH: "wisman",
        LEMMA: "wisatawan mancanegara",
        NORM: "wisatawan mancanegara"},
    {
        ORTH: "WIT",
        LEMMA: "Waktu Indonesia Timur",
        NORM: "Waktu Indonesia Timur"},
    {
        ORTH: "WITA",
        LEMMA: "Waktu Indonesia Tengah",
        NORM: "Waktu Indonesia Tengah"},
    {
        ORTH: "WNA",
        LEMMA: "warga negara asing",
        NORM: "warga negara asing"},
    {
        ORTH: "WNI",
        LEMMA: "warga negara Indonesia",
        NORM: "warga negara Indonesia"},
    {
        ORTH: "ybs.",
        LEMMA: "yang bersangkutan",
        NORM: "yang bersangkutan"}]:
    _exc[exc_data[ORTH]] = [exc_data]

_other_exc = {
    "do'a": [{ORTH: "do'a", LEMMA: "doa", NORM: "doa"}],
    "jum'at": [{ORTH: "jum'at", LEMMA: "Jumat", NORM: "Jumat"}],
    "Jum'at": [{ORTH: "Jum'at", LEMMA: "Jumat", NORM: "Jumat"}],
    "la'nat": [{ORTH: "la'nat", LEMMA: "laknat", NORM: "laknat"}],
    "ma'af": [{ORTH: "ma'af", LEMMA: "maaf", NORM: "maaf"}],
    "mu'jizat": [{ORTH: "mu'jizat", LEMMA: "mukjizat", NORM: "mukjizat"}],
    "Mu'jizat": [{ORTH: "Mu'jizat", LEMMA: "mukjizat", NORM: "mukjizat"}],
    "ni'mat": [{ORTH: "ni'mat", LEMMA: "nikmat", NORM: "nikmat"}],
    "raka'at": [{ORTH: "raka'at", LEMMA: "rakaat", NORM: "rakaat"}],
    "ta'at": [{ORTH: "ta'at", LEMMA: "taat", NORM: "taat"}],
}

_exc.update(_other_exc)

for orth in [
    "A.AB.", "A.Ma.", "A.Md.", "A.Md.Keb.", "A.Md.Kep.", "A.P.",
    "B.A.", "B.Ch.E.", "B.Sc.", "Dr.", "Dra.", "Drs.", "Hj.", "Ka.", "Kp.",
    "M.AB", "M.Ag.", "M.AP", "M.Arl", "M.A.R.S", "M.Hum.", "M.I.Kom.",
    "M.Kes,", "M.Kom.", "M.M.", "M.P.", "M.Pd.", "M.Psi.", "M.Psi.T.", "M.Sc.",
    "M.SArl", "M.Si.", "M.Sn.", "M.T.", "M.Th.", "No.", "Pjs.", "Plt.", "R.A.",
    "S.AB", "S.AP", "S.Adm", "S.Ag.", "S.Agr", "S.Ant", "S.Arl", "S.Ars",
    "S.A.R.S", "S.Ds", "S.E.", "S.E.I.", "S.Farm", "S.Gz.", "S.H.", "S.Han",
    "S.H.Int", "S.Hum", "S.Hut.", "S.In.", "S.IK.", "S.I.Kom.", "S.I.P",
    "S.IP", "S.P.", "S.Pt", "S.Psi", "S.Ptk", "S.Keb", "S.Ked", "S.Kep",
    "S.KG", "S.KH", "S.Kel", "S.K.M.", "S.Kedg.", "S.Kedh.", "S.Kom.", "S.KPM",
    "S.Mb", "S.Mat", "S.Par", "S.Pd.", "S.Pd.I.", "S.Pd.SD", "S.Pol.",
    "S.Psi.", "S.S.", "S.SArl.", "S.Sn", "S.Si.", "S.Si.Teol.", "S.SI.",
    "S.ST.", "S.ST.Han", "S.STP", "S.Sos.", "S.Sy.", "S.T.", "S.T.Han",
    "S.Th.", "S.Th.I" "S.TI.", "S.T.P.", "S.TrK", "S.Tekp.", "S.Th.",
    "Prof.", "drg.", "KH.", "Ust.", "Lc", "Pdt.", "S.H.H.", "Rm.", "Ps.",
    "St.", "M.A.", "M.B.A", "M.Eng.", "M.Eng.Sc.", "M.Pharm.", "Dr. med",
    "Dr.-Ing", "Dr. rer. nat.", "Dr. phil.", "Dr. iur.", "Dr. rer. oec",
    "Dr. rer. pol.", "R.Ng.", "R.", "R.M.", "R.B.", "R.P.", "R.Ay.", "Rr.",
    "R.Ngt.", "a.l.", "a.n.", "a.s.", "b.d.", "d.a.", "d.l.", "d/h", "dkk.",
    "dll.", "dr.", "drh.", "ds.", "dsb.", "dst.", "faks.", "fax.", "hlm.",
    "i/o", "n.b.", "p.p." "pjs.", "s.d.", "tel.", "u.p."]:
    _exc[orth] = [{ORTH: orth}]

TOKENIZER_EXCEPTIONS = _exc
