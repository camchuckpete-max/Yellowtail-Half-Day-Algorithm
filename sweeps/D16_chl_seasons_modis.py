# Goal D sweep 16 (D-055, descriptive): season-level chlorophyll vs yellowtail hit rate, extended to 2010-2011
# with MODIS-Aqua (erdMH1chla1day). Overlap summers 2012-2013 (MODIS and SNPP VIIRS) give the sensor offset.
# Uses Jul-Oct mean log chl over t_sd_coast straight from conditions_daily (a season summary, not a trip feature).
import sys; sys.path.insert(0, '.')
import numpy as np, pandas as pd
from yt import trips, source
df, man = trips.build()
db = source.open_db(man)
c = pd.read_sql("SELECT condition_date, source, chl FROM conditions_daily WHERE zone_id='t_sd_coast' AND chl > 0", db)
c["date"] = pd.to_datetime(c["condition_date"]); c["yr"] = c.date.dt.year
c = c[c.date.dt.month.between(7, 10)]
c["logchl"] = np.log(c["chl"])
s = c.groupby(["yr", "source"])["logchl"].agg(["mean", "size"]).unstack("source")
print(f"# descriptive only; source {man['source_commit'][:7]}")
print("Jul-Oct mean log chl (t_sd_coast) and day counts by sensor:")
print(s.round(3).to_string())
ov = s["mean"][["erdMH1chla1day", "noaacwNPPVIIRSSQchlaDaily"]].dropna()
offset = float((ov["noaacwNPPVIIRSSQchlaDaily"] - ov["erdMH1chla1day"]).mean())
print(f"\noverlap years {list(ov.index)}: VIIRS - MODIS offset (log) = {offset:+.3f} (x{np.exp(offset):.2f})")
viirs = s["mean"]["noaacwNPPVIIRSSQchlaDaily"].combine_first(s["mean"].get("noaacwN20VIIRSchlaDaily"))
modis_adj = s["mean"]["erdMH1chla1day"] + offset
season = viirs.combine_first(modis_adj)
d = df[(df.trip_twilight == 0) & df.date.dt.month.between(7, 10) & df.date.dt.year.between(2010, 2023)].copy()
d["pier_F"] = d["hc_pier_wtmp_24h"] * 9 / 5 + 32
yl = pd.DataFrame({"chl_mg": np.exp(season), "sensor": ["MODIS(adj)" if pd.isna(viirs.get(y)) else "VIIRS" for y in season.index]})
yl["all_rate"] = d.groupby(d.date.dt.year)["y"].mean()
yl["warm_rate"] = d[d.pier_F >= 68].groupby(d.date.dt.year)["y"].mean()
yl["pier_F"] = d.groupby(d.date.dt.year)["pier_F"].mean()
yl = yl.loc[2010:2023]
print("\nJul-Oct season table:")
print(yl.round(3).to_string())
for lab, t in (("2010-2023 (14 seasons)", yl), ("2012-2023 (VIIRS only, as D-052)", yl.loc[2012:]),
               ("2010-2020 (MODIS adj + SNPP)", yl.loc[:2020])):
    print(f"{lab}: Spearman chl vs all {np.log(t.chl_mg).corr(t.all_rate, method='spearman'):.2f}, "
          f"vs warm {np.log(t.chl_mg).corr(t.warm_rate, method='spearman'):.2f}; pier vs all {t.pier_F.corr(t.all_rate, method='spearman'):.2f}")
# Does season chl add to season pier temperature? Rank-based partial correlation (residuals of ranks).
r = yl[["chl_mg", "pier_F", "all_rate", "warm_rate"]].rank()
def partial(a, b, ctrl):
    ra = r[a] - np.polyval(np.polyfit(r[ctrl], r[a], 1), r[ctrl]); rb = r[b] - np.polyval(np.polyfit(r[ctrl], r[b], 1), r[ctrl])
    return float(np.corrcoef(ra, rb)[0, 1])
print(f"\npartial Spearman, 14 seasons: chl vs all_rate | pier {partial('chl_mg', 'all_rate', 'pier_F'):+.2f}; "
      f"pier vs all_rate | chl {partial('pier_F', 'all_rate', 'chl_mg'):+.2f}; chl vs pier {r.chl_mg.corr(r.pier_F):+.2f}")
print(f"partial Spearman, 14 seasons: chl vs warm_rate | pier {partial('chl_mg', 'warm_rate', 'pier_F'):+.2f}")
