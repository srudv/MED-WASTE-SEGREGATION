"""Reusable chart generation for CPCB biomedical-waste analytics (2023)."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_DATA=ROOT/"data/processed/medical_waste_cleaned.csv"
DEFAULT_OUT=ROOT/"reports/figures"

def load_visualization_data(path=DEFAULT_DATA):
    df=pd.read_csv(path)
    if len(df)!=37 or "state_ut" not in df: raise ValueError("Expected 37 reporting entities")
    for c in df.columns:
        if c!="state_ut": df[c]=pd.to_numeric(df[c],errors="coerce")
    return df

def generate_all_charts(data=None, output_dir=DEFAULT_OUT, formats=("png","svg")):
    d=load_visualization_data() if data is None else data.copy()
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    for c in d.columns:
        if c!="state_ut": d[c]=pd.to_numeric(d[c],errors="coerce")
    paths=[]
    def save(fig,stem):
        for ext in formats:
            p=output_dir/f"{stem}.{ext}"
            fig.savefig(p,dpi=180,bbox_inches="tight",format=ext)
            paths.append(p)
        plt.close(fig)
    top=d.nlargest(10,"bmw_generated_kg_day").sort_values("bmw_generated_kg_day")
    fig,ax=plt.subplots(figsize=(10,6)); ax.barh(top.state_ut,top.bmw_generated_kg_day)
    ax.set(title="Top 10 biomedical waste generators",xlabel="Waste generated (kg/day)",ylabel="Reporting entity"); save(fig,"01_top10_waste_generators")
    top=d.nlargest(10,"bmw_generated_kg_day").sort_values("bmw_generated_kg_day")
    fig,ax=plt.subplots(figsize=(10,6)); y=range(len(top))
    ax.barh([i-.18 for i in y],top.bmw_generated_kg_day,height=.35,label="Generated")
    ax.barh([i+.18 for i in y],top.bmw_treated_disposed_kg_day,height=.35,label="Treated/disposed")
    ax.set_yticks(list(y),top.state_ut); ax.set(title="Generated vs treated/disposed — top 10",xlabel="kg/day",ylabel="Reporting entity"); ax.legend(); save(fig,"02_generated_vs_treated")
    fig,ax=plt.subplots(figsize=(7,7)); route=d[["bmw_treated_captive_kg_day","bmw_treated_cbwtf_kg_day"]].sum()
    ax.pie(route,labels=["Captive","CBWTF"],autopct="%1.1f%%",startangle=90,wedgeprops={"width":.42}); ax.set_title("Reported treatment route distribution"); save(fig,"03_treatment_route_donut")
    fig,ax=plt.subplots(figsize=(9,5)); ax.hist(d.bmw_generated_kg_day.dropna(),bins=10)
    ax.set(title="Distribution of waste generation",xlabel="Waste generated (kg/day)",ylabel="Reporting entities"); save(fig,"04_generation_histogram")
    fig,ax=plt.subplots(figsize=(8,6)); ax.scatter(d.total_hcfs,d.bmw_generated_kg_day)
    ax.set(title="Healthcare facilities vs waste generation",xlabel="Total healthcare facilities",ylabel="Waste generated (kg/day)"); save(fig,"05_facilities_vs_generation_scatter")
    fig,ax=plt.subplots(figsize=(8,4)); infra=d[["cbwtfs_operational","cbwtfs_under_construction"]].sum()
    ax.bar(["Operational","Under construction"],infra.values); ax.set(title="CBWTF infrastructure status",ylabel="Number of facilities"); save(fig,"06_cbwtf_infrastructure")
    v=d.dropna(subset=["violations_hcf_cbwtf"]).nlargest(10,"violations_hcf_cbwtf").sort_values("violations_hcf_cbwtf")
    fig,ax=plt.subplots(figsize=(10,6)); ax.barh(v.state_ut,v.violations_hcf_cbwtf)
    ax.set(title="Top 10 reported violations",xlabel="Recorded violations",ylabel="Reporting entity"); save(fig,"07_top10_violations")
    return paths

if __name__=="__main__":
    for p in generate_all_charts(): print(p)
