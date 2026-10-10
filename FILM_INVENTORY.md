# FILM INVENTORY
Last update: 2026-10-10
Label column: **Lude chooses** (PNT, OYE Prod, or both). Case by case, no "by extension".

## 0. Film counts (checked 2026-10-10)

Films total: 99
Films online: 87

| Source | Films | Detail |
|---|---|---|
| **ponadto.foundation** (Wix CMS, collection "Workshops Po-Nad-To") | **99** | **87 published**, 12 hidden: 9 "Life Polska" campaign shorts, "La Ville des Rois" + its clip, "Pytki - Jedna Droga". Years 2013 to 2026. |
| Notion "SITE PO-NAD-TO / Video List" | 100 rows (96 marked Film) | Working list only, not used for counts. |
| **oyeprod.com** | **18** | 17 films + showreel (section 1 below), confirmed by Lude 10 Oct 2026. A selection, most also on the PNT site. |

**Wix is the actual number** (Lude, 10 Oct 2026). Always count films from the Wix CMS, never from Notion or local files. The dashboard shows "Films total" and "Films online" from the two lines above.

## 1. Films on oyeprod.com (18)

Source: `1_PNT_OYE /5_ID/Site_OYEProd_2025-2026/OYE FILMS/Films_OYE_site.odt`

| # | Title | Caption | Year | Length | Label | Link |
|---|---|---|---|---|---|---|
| 0 | OYE Prod showreel | Showreel | TO CHECK | 1:05 | OYE Prod | https://youtu.be/DcRLkk99guY |
| 1 | Igrzyska Wolności 2018 | Liberté! | 2018 | 1:35 | TO CHOOSE | https://youtu.be/mxPSJKi8vS4 |
| 2 | United CVE Poland | OSCE | TO CHECK | 2:12 | TO CHOOSE | https://youtu.be/vPdj3SQuXPo |
| 3 | My OC | One Caucasus | 2020 | 15:45 | TO CHOOSE | https://youtu.be/74LN_A7Whis |
| 4 | Chicas Unidas | Bacalar, Mexico | TO CHECK | 1:29 | TO CHOOSE | https://youtu.be/9XnyDhbAjFo |
| 5 | PIH Nursing | Partners In Health | TO CHECK | 1:00 | TO CHOOSE | https://youtube.com/shorts/Rs5pouMAwAI |
| 6 | Sokole Ranczo | Spot | TO CHECK | 1:34 | TO CHOOSE | https://youtu.be/FpnBALTq9Bs |
| 7 | Amaia Artwalk Chomiczówka | Warsaw | TO CHECK | 9:53 | TO CHOOSE | https://youtu.be/fU5uKyVThjk |
| 8 | Business Unusual | Stocznia | TO CHECK | 0:58 | TO CHOOSE | https://youtu.be/Jz8cXc4hxrI |
| 9 | Baltic Sea | European Liberal Forum | TO CHECK | 3:52 | TO CHOOSE | https://youtu.be/Bq3kQuqYJYU |
| 10 | Ruslam | OSCE LIVE | TO CHECK | 0:56 | TO CHOOSE | https://youtu.be/nHzsVPv5-cM |
| 11 | Vaxhide | OSCE LIVE | TO CHECK | 1:21 | TO CHOOSE | https://youtu.be/QQ2Sq3bsqhY |
| 12 | Carys | OSCE LIVE | TO CHECK | 1:22 | TO CHOOSE | https://youtu.be/MkyuCOEnm1s |
| 13 | Akcja Integracja | Poland | 2023 | 6:52 | TO CHOOSE | https://youtu.be/oDpe7Swe6SA |
| 14 | Mental Health | Projekt: Polska | TO CHECK | 0:58 | TO CHOOSE | https://youtu.be/1CZNOPWrVXU |
| 15 | Goszczyn | KGW | TO CHECK | 7:36 | TO CHOOSE | https://youtu.be/_iFpL-LG-9M |
| 16 | JA i JUTRA | IBE | TO CHECK | 1:29 | TO CHOOSE | https://youtu.be/peqWZ-w5O6c |
| 17 | Edukacja dla Wolności | (no caption) | TO CHECK | 2:23 | TO CHOOSE | https://youtu.be/zwLuxBMny20 |

## 2. Other films found on this Mac

| Title | Project | Path |
|---|---|---|
| Cine Village Explainer (2 versions) | SAINT LUCIA | `3_CINE VILLAGE/CINE VILLAGE PROCESS 2026/COM/` |
| PIH I Reel 1 (Judy N. Khanyola) and Reel 2 (Alison Lutz) | OYE Prod / PIH | `5_ID/Site_OYEProd_2025-2026/OYE FILMS/` |
| Holbox - The Icon | TO CHECK | same folder |
| BU Lublin 2023 | TO CHECK | same folder |
| Demo OYE 26.04.2024 | OYE Prod | same folder |
| Lude Promo Record | OYAI | `4_OYAI/OYAI PROMO/OYAI PRESENTATION+MARKETING/` |

## 3. TO CHECK: keep every film list in sync

Whenever a film is found, added, relabelled or removed, update **all** of these places, in this order:

| # | Place | What to update | How |
|---|---|---|---|
| 1 | This file (`FILM_INVENTORY.md`) | Row, label, year, link | Edit here first: this is the master list |
| 2 | `5_ID/Site_OYEProd_2025-2026/OYE FILMS/Films_OYE_site.odt` | Order, Show yes/no, captions, link | Only for films shown on oyeprod.com |
| 3 | oyeprod.com | Rebuild and deploy | `python3 build.py`, then Vercel deploy (see the OYE site recap) |
| 4 | "OYE Prod" preview artifact | Republish after the site changes | claude.ai/artifact/7i9KYktpH7GiPbsHsGxtQ9 |
| 5 | Wix CMS (99 film entries) | Same title, label, link | Lude does it by hand (no agent writes to Wix) |
| 6 | Thumbnails `Thumbs/` | New thumbnail if needed | Lude, by hand in Canva |
| 7 | State files | "Content ready to show" in `states/OYE_STATE.md` / `PNT_STATE.md` / `SAINTLUCIA_STATE.md` | LUDIZM STATE UPDATE |
| 8 | `LUDIZM_DASHBOARD.md` | Film count | LUDIZM STATE UPDATE |

Open checks:
- [x] Count the Wix CMS films: 99 entries, 87 published (10 Oct 2026).
- [ ] Find "Liberté, égalité, fraternité" (Saint-Denis) and "One small flame is enough".
- [ ] Lude chooses a label for each film (PNT / OYE Prod / both).
- [ ] Years marked TO CHECK in section 1.

## 4. Still to find

- **"Liberté, égalité, fraternité" (Saint-Denis)** and **"One small flame is enough"** (six days, ten young people): not found on this Mac. Probably on an external drive or YouTube. TO CHECK
- The Wix CMS lists **99 film entries**. Most are not on this Mac. Export that list to complete this inventory.

Note: 284 video files exist under `PNT - OYE/`. Most are screen recordings, workshop exercises and AI test clips, not films, so they are not listed here.
