"""Lithium supply-chain MILP - the Energies 2024 paper model.

Extracted verbatim from jupyter_folder_original/Lithium_UFL_Energies.ipynb
(SHA-256 2aca0eec...), whose model.mps matches the dimensions the paper reports:
13,556 rows and 10,706 continuous variables.

ONE class of change from the notebook, and it is what makes it runnable: every
input path was an absolute literal under a Downloads folder that exists on no
current machine. Paths are now DERIVED from this file's location. The model
itself is untouched.

Paper: Jones, E.C., Jr. "Lithium Supply Chain Optimization: A Global Analysis of
Critical Minerals for Batteries." Energies 2024, 17, 2685.
https://doi.org/10.3390/en17112685
"""
import pandas as pd

from .paths import DATA_DIR, RESULTS_DIR, check_data_dir   # noqa: F401  (paths live apart from the model)

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _csv(name):
    """Read an input CSV case-insensitively.

    The notebook asks for 'Cath_fixed_CO2.csv'; the folder holds
    'cath_fixed_CO2.csv'. Windows hides that mismatch, Linux does not - so the
    original code fails on Colab and in CI. Resolved here rather than by
    renaming the paper's own data files.
    """
    check_data_dir(DATA_DIR)
    p = DATA_DIR / name
    if p.exists():
        return pd.read_csv(p)
    want = name.lower()
    for f in DATA_DIR.iterdir():
        if f.name.lower() == want:
            return pd.read_csv(f)
    raise FileNotFoundError(name + " not found in " + str(DATA_DIR))


# install gurobipy pip install gurobipy  



# ---- cell ----
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import io


# ---- cell ----
# Warehouse_data_url = "https://raw.githubusercontent.com/Raziye-Aghapour/OR_Class_Fall2023/main/Warehouse_data.csv"
# Warehouse_data = pd.read_csv(Warehouse_data_url )

# Demand_data_url="https://raw.githubusercontent.com/Raziye-Aghapour/OR_Class_Fall2023/main/Demand.csv"
# Demand_data = pd.read_csv(Demand_data_url )

# Shipping_data_url="https://raw.githubusercontent.com/Raziye-Aghapour/OR_Class_Fall2023/main/Shipping_cost.csv"
# Shipping_data = pd.read_csv(Shipping_data_url )

##Alternative way to import data
#Warehouse_data = pd.read_csv(io.BytesIO(Warehouse_data_uploaded['Warehouse_data.csv']))

# Warehouse_data

# ---- cell ----
Index = _csv('index.csv')



# ---- cell ----
# Warehouses
#W= list(Warehouse_data['Warehouse'])

# Years
Y = list(Index['Year'])
Y = [x for x in Y if str(x) != 'nan']

Y_warm = list(range(2025,2101))
Y_start = [2020, 2021, 2022, 2023, 2024]

# Stage
S = list(Index['Stage'])
S = [x for x in S if str(x) != 'nan']

# Region
R = list(Index['Region'])
R = [x for x in R if str(x) != 'nan']

# Technology
T = list(Index['Technology'])
T = [x for x in T if str(x) != 'nan']


print(T)

# ---- cell ----
Mine_Demand = _csv('mine_demand.csv')

Proc_Demand = _csv('proc_demand.csv')

Cath_Demand = _csv('cath_demand.csv')

Cell_Demand = _csv('cell_demand.csv')

Pack_Demand = _csv('pack_demand.csv')

Rec_Demand = _csv('rec_demand.csv')

# ---- cell ----
# Demand

YS_mine, mine_demand = gp.multidict((Mine_Demand.set_index(zip(Mine_Demand['Year'], Mine_Demand['Stage'])))['Demand'].to_dict())

YST_proc, proc_demand = gp.multidict((Proc_Demand.set_index(zip(Proc_Demand['Year'], Proc_Demand['Stage'], Proc_Demand['Technology'])))['Demand'].to_dict())

YST_cath, cath_demand = gp.multidict((Cath_Demand.set_index(zip(Cath_Demand['Year'], Cath_Demand['Stage'], Cath_Demand['Technology'])))['Demand'].to_dict())

YST_cell, cell_demand = gp.multidict((Cell_Demand.set_index(zip(Cell_Demand['Year'], Cell_Demand['Stage'], Cell_Demand['Technology'])))['Demand'].to_dict())

YST_pack, pack_demand = gp.multidict((Pack_Demand.set_index(zip(Pack_Demand['Year'], Pack_Demand['Stage'], Pack_Demand['Technology'])))['Demand'].to_dict())

YST_rec, rec_demand = gp.multidict((Rec_Demand.set_index(zip(Rec_Demand['Year'], Rec_Demand['Stage'], Rec_Demand['Technology'])))['Demand'].to_dict())

# ---- cell ----
Mine_Prod_Cost = _csv('mine_prod_cost.csv')

Mine_Var_Cost = _csv('mine_var_cost.csv')

Mine_Fixed_Cost = _csv('mine_fixed_cost.csv')

# ---- cell ----
Mine_Prod_CO2 = _csv('mine_prod_CO2.csv')

Mine_Var_CO2 = _csv('mine_var_CO2.csv')

Mine_Fixed_CO2 = _csv('mine_fixed_CO2.csv')

# ---- cell ----
# Mine Costs

YST_mine, mine_prod_cost = gp.multidict((Mine_Prod_Cost.set_index(zip(Mine_Prod_Cost['Year'], Mine_Prod_Cost['Stage'], Mine_Prod_Cost['Technology'])))['Cost'].to_dict())

YST_mine, mine_fixed_cost = gp.multidict((Mine_Fixed_Cost.set_index(zip(Mine_Fixed_Cost['Year'], Mine_Fixed_Cost['Stage'], Mine_Fixed_Cost['Technology'])))['Cost'].to_dict())

YST_mine, mine_var_cost = gp.multidict((Mine_Var_Cost.set_index(zip(Mine_Var_Cost['Year'], Mine_Var_Cost['Stage'], Mine_Var_Cost['Technology'])))['Cost'].to_dict())


# ---- cell ----
# Mine CO2s

YST_mine, mine_prod_CO2 = gp.multidict((Mine_Prod_CO2.set_index(zip(Mine_Prod_CO2['Year'], Mine_Prod_CO2['Stage'], Mine_Prod_CO2['Technology'])))['CO2'].to_dict())

YST_mine, mine_fixed_CO2 = gp.multidict((Mine_Fixed_CO2.set_index(zip(Mine_Fixed_CO2['Year'], Mine_Fixed_CO2['Stage'], Mine_Fixed_CO2['Technology'])))['CO2'].to_dict())

YST_mine, mine_var_CO2 = gp.multidict((Mine_Var_CO2.set_index(zip(Mine_Var_CO2['Year'], Mine_Var_CO2['Stage'], Mine_Var_CO2['Technology'])))['CO2'].to_dict())


# ---- cell ----
Proc_Prod_Cost = _csv('Proc_prod_cost.csv')

Proc_Var_Cost = _csv('Proc_var_cost.csv')

Proc_Fixed_Cost = _csv('Proc_fixed_cost.csv')

# ---- cell ----
Proc_Prod_CO2 = _csv('Proc_prod_CO2.csv')

Proc_Var_CO2 = _csv('Proc_var_CO2.csv')

Proc_Fixed_CO2 = _csv('Proc_fixed_CO2.csv')

# ---- cell ----
YSIO_proc, proc_prod_cost = gp.multidict((Proc_Prod_Cost.set_index(zip(Proc_Prod_Cost['Year'], Proc_Prod_Cost['Stage'], Proc_Prod_Cost['Input'], Proc_Prod_Cost['Output'] )))['Cost'].to_dict())

YSIO_proc, proc_fixed_cost = gp.multidict((Proc_Fixed_Cost.set_index(zip(Proc_Fixed_Cost['Year'], Proc_Fixed_Cost['Stage'], Proc_Fixed_Cost['Input'], Proc_Fixed_Cost['Output'])))['Cost'].to_dict())

YSIO_proc, proc_var_cost = gp.multidict((Proc_Var_Cost.set_index(zip(Proc_Var_Cost['Year'], Proc_Var_Cost['Stage'], Proc_Var_Cost['Input'], Proc_Var_Cost['Output'])))['Cost'].to_dict())

# ---- cell ----
YSIO_proc, proc_prod_CO2 = gp.multidict((Proc_Prod_CO2.set_index(zip(Proc_Prod_CO2['Year'], Proc_Prod_CO2['Stage'], Proc_Prod_CO2['Input'], Proc_Prod_CO2['Output'] )))['CO2'].to_dict())

YSIO_proc, proc_fixed_CO2 = gp.multidict((Proc_Fixed_CO2.set_index(zip(Proc_Fixed_CO2['Year'], Proc_Fixed_CO2['Stage'], Proc_Fixed_CO2['Input'], Proc_Fixed_CO2['Output'])))['CO2'].to_dict())

YSIO_proc, proc_var_CO2 = gp.multidict((Proc_Var_CO2.set_index(zip(Proc_Var_CO2['Year'], Proc_Var_CO2['Stage'], Proc_Var_CO2['Input'], Proc_Var_CO2['Output'])))['CO2'].to_dict())

# ---- cell ----
Cath_Prod_Cost = _csv('Cath_prod_cost.csv')

Cath_Var_Cost = _csv('Cath_var_cost.csv')

Cath_Fixed_Cost = _csv('Cath_fixed_cost.csv')

# ---- cell ----
Cath_Prod_CO2 = _csv('Cath_prod_CO2.csv')

Cath_Var_CO2 = _csv('Cath_var_CO2.csv')

Cath_Fixed_CO2 = _csv('Cath_fixed_CO2.csv')

# ---- cell ----
YSIO_cath, cath_prod_cost = gp.multidict((Cath_Prod_Cost.set_index(zip(Cath_Prod_Cost['Year'], Cath_Prod_Cost['Stage'], Cath_Prod_Cost['Input'], Cath_Prod_Cost['Output'] )))['Cost'].to_dict())

YSIO_cath, cath_fixed_cost = gp.multidict((Cath_Fixed_Cost.set_index(zip(Cath_Fixed_Cost['Year'], Cath_Fixed_Cost['Stage'], Cath_Fixed_Cost['Input'], Cath_Fixed_Cost['Output'])))['Cost'].to_dict())

YSIO_cath, cath_var_cost = gp.multidict((Cath_Var_Cost.set_index(zip(Cath_Var_Cost['Year'], Cath_Var_Cost['Stage'], Cath_Var_Cost['Input'], Cath_Var_Cost['Output'])))['Cost'].to_dict())

# ---- cell ----
YSIO_cath, cath_prod_CO2 = gp.multidict((Cath_Prod_CO2.set_index(zip(Cath_Prod_CO2['Year'], Cath_Prod_CO2['Stage'], Cath_Prod_CO2['Input'], Cath_Prod_CO2['Output'] )))['CO2'].to_dict())

YSIO_cath, cath_fixed_CO2 = gp.multidict((Cath_Fixed_CO2.set_index(zip(Cath_Fixed_CO2['Year'], Cath_Fixed_CO2['Stage'], Cath_Fixed_CO2['Input'], Cath_Fixed_CO2['Output'])))['CO2'].to_dict())

YSIO_cath, cath_var_CO2 = gp.multidict((Cath_Var_CO2.set_index(zip(Cath_Var_CO2['Year'], Cath_Var_CO2['Stage'], Cath_Var_CO2['Input'], Cath_Var_CO2['Output'])))['CO2'].to_dict())

# ---- cell ----
Cell_Prod_Cost = _csv('Cell_prod_cost.csv')

Cell_Var_Cost = _csv('Cell_var_cost.csv')

Cell_Fixed_Cost = _csv('Cell_fixed_cost.csv')

# ---- cell ----
Cell_Prod_CO2 = _csv('Cell_prod_CO2.csv')

Cell_Var_CO2 = _csv('Cell_var_CO2.csv')

Cell_Fixed_CO2 = _csv('Cell_fixed_CO2.csv')

# ---- cell ----
YSIO_cell, cell_prod_cost = gp.multidict((Cell_Prod_Cost.set_index(zip(Cell_Prod_Cost['Year'], Cell_Prod_Cost['Stage'], Cell_Prod_Cost['Input'], Cell_Prod_Cost['Output'] )))['Cost'].to_dict())

YSIO_cell, cell_fixed_cost = gp.multidict((Cell_Fixed_Cost.set_index(zip(Cell_Fixed_Cost['Year'], Cell_Fixed_Cost['Stage'], Cell_Fixed_Cost['Input'], Cell_Fixed_Cost['Output'])))['Cost'].to_dict())

YSIO_cell, cell_var_cost = gp.multidict((Cell_Var_Cost.set_index(zip(Cell_Var_Cost['Year'], Cell_Var_Cost['Stage'], Cell_Var_Cost['Input'], Cell_Var_Cost['Output'])))['Cost'].to_dict())

# ---- cell ----
YSIO_cell, cell_prod_CO2 = gp.multidict((Cell_Prod_CO2.set_index(zip(Cell_Prod_CO2['Year'], Cell_Prod_CO2['Stage'], Cell_Prod_CO2['Input'], Cell_Prod_CO2['Output'] )))['CO2'].to_dict())

YSIO_cell, cell_fixed_CO2 = gp.multidict((Cell_Fixed_CO2.set_index(zip(Cell_Fixed_CO2['Year'], Cell_Fixed_CO2['Stage'], Cell_Fixed_CO2['Input'], Cell_Fixed_CO2['Output'])))['CO2'].to_dict())

YSIO_cell, cell_var_CO2 = gp.multidict((Cell_Var_CO2.set_index(zip(Cell_Var_CO2['Year'], Cell_Var_CO2['Stage'], Cell_Var_CO2['Input'], Cell_Var_CO2['Output'])))['CO2'].to_dict())

# ---- cell ----
Pack_Prod_Cost = _csv('Pack_prod_cost.csv')

Pack_Var_Cost = _csv('Pack_var_cost.csv')

Pack_Fixed_Cost = _csv('Pack_fixed_cost.csv')

# ---- cell ----
Pack_Prod_CO2 = _csv('Pack_prod_CO2.csv')

Pack_Var_CO2 = _csv('Pack_var_CO2.csv')

Pack_Fixed_CO2 = _csv('Pack_fixed_CO2.csv')

# ---- cell ----
YSIO_pack, pack_prod_cost = gp.multidict((Pack_Prod_Cost.set_index(zip(Pack_Prod_Cost['Year'], Pack_Prod_Cost['Stage'], Pack_Prod_Cost['Input'], Pack_Prod_Cost['Output'] )))['Cost'].to_dict())

YSIO_pack, pack_fixed_cost = gp.multidict((Pack_Fixed_Cost.set_index(zip(Pack_Fixed_Cost['Year'], Pack_Fixed_Cost['Stage'], Pack_Fixed_Cost['Input'], Pack_Fixed_Cost['Output'])))['Cost'].to_dict())

YSIO_pack, pack_var_cost = gp.multidict((Pack_Var_Cost.set_index(zip(Pack_Var_Cost['Year'], Pack_Var_Cost['Stage'], Pack_Var_Cost['Input'], Pack_Var_Cost['Output'])))['Cost'].to_dict())

# ---- cell ----
YSIO_pack, pack_prod_CO2 = gp.multidict((Pack_Prod_CO2.set_index(zip(Pack_Prod_CO2['Year'], Pack_Prod_CO2['Stage'], Pack_Prod_CO2['Input'], Pack_Prod_CO2['Output'] )))['CO2'].to_dict())

YSIO_pack, pack_fixed_CO2 = gp.multidict((Pack_Fixed_CO2.set_index(zip(Pack_Fixed_CO2['Year'], Pack_Fixed_CO2['Stage'], Pack_Fixed_CO2['Input'], Pack_Fixed_CO2['Output'])))['CO2'].to_dict())

YSIO_pack, pack_var_CO2 = gp.multidict((Pack_Var_CO2.set_index(zip(Pack_Var_CO2['Year'], Pack_Var_CO2['Stage'], Pack_Var_CO2['Input'], Pack_Var_CO2['Output'])))['CO2'].to_dict())

# ---- cell ----
Rec_Prod_Cost = _csv('Rec_prod_cost.csv')

Rec_Var_Cost = _csv('Rec_var_cost.csv')

Rec_Fixed_Cost = _csv('Rec_fixed_cost.csv')

# ---- cell ----
Rec_Prod_CO2 = _csv('Rec_prod_CO2.csv')

Rec_Var_CO2 = _csv('Rec_var_CO2.csv')

Rec_Fixed_CO2 = _csv('Rec_fixed_CO2.csv')

# ---- cell ----
YSIO_rec, rec_prod_cost = gp.multidict((Rec_Prod_Cost.set_index(zip(Rec_Prod_Cost['Year'], Rec_Prod_Cost['Stage'], Rec_Prod_Cost['Input'], Rec_Prod_Cost['Output'] )))['Cost'].to_dict())

YSIO_rec, rec_fixed_cost = gp.multidict((Rec_Fixed_Cost.set_index(zip(Rec_Fixed_Cost['Year'], Rec_Fixed_Cost['Stage'], Rec_Fixed_Cost['Input'], Rec_Fixed_Cost['Output'])))['Cost'].to_dict())

YSIO_rec, rec_var_cost = gp.multidict((Rec_Var_Cost.set_index(zip(Rec_Var_Cost['Year'], Rec_Var_Cost['Stage'], Rec_Var_Cost['Input'], Rec_Var_Cost['Output'])))['Cost'].to_dict())

# ---- cell ----
YSIO_rec, rec_prod_CO2 = gp.multidict((Rec_Prod_CO2.set_index(zip(Rec_Prod_CO2['Year'], Rec_Prod_CO2['Stage'], Rec_Prod_CO2['Input'], Rec_Prod_CO2['Output'] )))['CO2'].to_dict())

YSIO_rec, rec_fixed_CO2 = gp.multidict((Rec_Fixed_CO2.set_index(zip(Rec_Fixed_CO2['Year'], Rec_Fixed_CO2['Stage'], Rec_Fixed_CO2['Input'], Rec_Fixed_CO2['Output'])))['CO2'].to_dict())

YSIO_rec, rec_var_CO2 = gp.multidict((Rec_Var_CO2.set_index(zip(Rec_Var_CO2['Year'], Rec_Var_CO2['Stage'], Rec_Var_CO2['Input'], Rec_Var_CO2['Output'])))['CO2'].to_dict())

# ---- cell ----
# Licence comes from the environment (gurobi.lic, WLS env vars, or the
# pip default licence) - never from literals in the source.
env = gp.Env()

# ---- cell ----
# Declare and initialize model
m=gp.Model("Lithium", env=env)

# ---- cell ----
#Create decision variables for the model

prod_mine = m.addVars(YST_mine, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'prod_mine')
prod_proc = m.addVars(YSIO_proc, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'prod_proc')
prod_cath = m.addVars(YSIO_cath, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'prod_cath')
prod_cell = m.addVars(YSIO_cell, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'prod_cell')
prod_pack = m.addVars(YSIO_pack, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'prod_pack')
prod_rec = m.addVars(YSIO_rec, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'prod_rec')







# ---- cell ----
#Mine Investment and Capacity Constraints
active_mine = m.addVars(YST_mine, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'active_mine')
invest_mine = m.addVars(YST_mine, lb = 0, ub = GRB.INFINITY, vtype = GRB.INTEGER, name = 'invest_mine')
new_capacity_mine = m.addVars(YST_mine, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'new_capacity_mine')
capacity_mine = m.addVars(YST_mine, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'capacity_mine')

# ---- cell ----
# Proc Investment and Capacity Constraints
active_proc = m.addVars(YSIO_proc, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'active_proc')
invest_proc = m.addVars(YSIO_proc, lb = 0, ub = GRB.INFINITY, vtype = GRB.INTEGER, name = 'invest_proc')
new_capacity_proc = m.addVars(YSIO_proc, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'new_capacity_proc')
capacity_proc = m.addVars(YSIO_proc, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'capacity_proc')

# ---- cell ----
# cath Investment and Capacity Constraints
active_cath = m.addVars(YSIO_cath, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'active_cath')
invest_cath = m.addVars(YSIO_cath, lb = 0, ub = GRB.INFINITY, vtype = GRB.INTEGER, name = 'invest_cath')
new_capacity_cath = m.addVars(YSIO_cath, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'new_capacity_cath')
capacity_cath = m.addVars(YSIO_cath, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'capacity_cath')

# ---- cell ----
# cell Investment and Capacity Constraints
active_cell = m.addVars(YSIO_cell, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'active_cell')
invest_cell = m.addVars(YSIO_cell, lb = 0, ub = GRB.INFINITY, vtype = GRB.INTEGER, name = 'invest_cell')
new_capacity_cell = m.addVars(YSIO_cell, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'new_capacity_cell')
capacity_cell = m.addVars(YSIO_cell, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'capacity_cell')

# ---- cell ----
# pack Investment and Capacity Constraints
active_pack = m.addVars(YSIO_pack, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'active_pack')
invest_pack = m.addVars(YSIO_pack, lb = 0, ub = GRB.INFINITY, vtype = GRB.INTEGER, name = 'invest_pack')
new_capacity_pack = m.addVars(YSIO_pack, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'new_capacity_pack')
capacity_pack = m.addVars(YSIO_pack, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'capacity_pack')

# ---- cell ----
# rec Investment and Capacity Constraints
active_rec = m.addVars(YSIO_rec, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'active_rec')
invest_rec = m.addVars(YSIO_rec, lb = 0, ub = GRB.INFINITY, vtype = GRB.INTEGER, name = 'invest_rec')
new_capacity_rec = m.addVars(YSIO_rec, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'new_capacity_rec')
capacity_rec = m.addVars(YSIO_rec, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'capacity_rec')

# ---- cell ----
# Deviation Variables as Needed

# d1 = m.addVars(Y, name = 'd1')
# d2 = m.addVars(Y, name = 'd2')
# d3 = m.addVars(Y, name = 'd3')
# d4 = m.addVars(Y, name = 'd4')
# d5 = m.addVars(Y, name = 'd5')

# ---- cell ----
T_mine = ['spod', 'brine', 'clay']
T_proc = ['lce', 'loh']
T_cath = ['nmc', 'lfp']
T_cell = ['GWh_nmc', 'GWh_lfp']
T_pack = ['bev_nmc', 'bev_lfp', 'phev_nmc', 'phev_lfp']
T_rec = ['lce', 'loh']

# ---- cell ----
lce_li = 5.324 # 5.234 kg (or kt) LCE / kg (or kt) Li
loh_li = 3.45101
GWh_nmc_kt_li = 8.11
GWh_lfp_kt_li = 10.58
GWh_bev = 62
GWh_phev = 15
max_new_units = 25

# ---- cell ----
demand_mine_constr = m.addConstrs((prod_mine.sum(y,'mine','*') + prod_rec.sum(y,'rec','*','lce') / lce_li + prod_rec.sum(y,'rec','*','loh') / loh_li >= mine_demand[y,'mine']  for y in Y) ,  name='demand_mine_constr')



# ---- cell ----
demand_proc_constr = m.addConstrs((prod_proc.sum(y,'proc','*',t) + prod_rec.sum(y,'rec', '*',t) >= proc_demand[y,'proc',t]  for y in Y for t in T_proc) ,  name='demand_proc_constr')
# Equivalent formulation but needs extra index
#demand_proc = m.addConstrs((gp.quicksum(prod_proc[y,'proc',i,t] for i in T_mine) >= proc_demand[y,'proc',t] for t in T_proc  for y in Y) , "demand_proc")

# ---- cell ----
demand_cath_constr = m.addConstrs((prod_cath.sum(y,'cath','*',t)  >= cath_demand[y,'cath',t]  for y in Y for t in T_cath) ,  name='demand_cath_constr')

# ---- cell ----
demand_cell_constr = m.addConstrs((prod_cell.sum(y,'cell','*',t)  >= cell_demand[y,'cell',t]  for y in Y for t in T_cell) ,  name='demand_cell_constr')

# ---- cell ----
demand_pack_constr = m.addConstrs((prod_pack.sum(y,'pack','*',t)  >= pack_demand[y,'pack',t]  for y in Y for t in T_pack) ,  name='demand_pack_constr')

# ---- cell ----
demand_rec_constr = m.addConstrs((prod_rec.sum(y,'rec','*',t)  <= rec_demand[y,'rec',t]  for y in Y for t in T_rec) ,  name='demand_rec_constr')

# ---- cell ----
link_mine_proc__lce = m.addConstrs((prod_proc[y,'proc',t,'lce'] <= lce_li * prod_mine[y,'mine',t]  for y in Y for t in T_mine) ,  name='link_mine_proc_lce')

# ---- cell ----
link_mine_proc__loh = m.addConstrs((prod_proc[y,'proc',t,'loh'] <= loh_li * prod_mine[y,'mine',t]  for y in Y for t in T_mine) ,  name='link_mine_proc_loh')

# ---- cell ----
link_proc_cath_nmc = m.addConstrs((loh_li * prod_cath[y,'cath',t,'nmc'] <= prod_proc.sum(y,'proc','*','loh') for y in Y for t in T_proc) ,  name='link_proc_cath_nmc')

# ---- cell ----
link_proc_cath_lfp = m.addConstrs(( lce_li * prod_cath[y,'cath',t,'lfp'] <= prod_proc.sum(y,'proc','*','lce') for y in Y for t in T_proc) ,  name='link_proc_cath_lfp')

# ---- cell ----
link_cath_cell_nmc = m.addConstrs((prod_cell[y,'cell',t,'GWh_nmc'] <=  GWh_nmc_kt_li * prod_cath.sum(y,'cath','*','nmc') for y in Y for t in T_cath) ,  name='link_cath_cell_nmc')

# ---- cell ----
link_cath_cell_lfp = m.addConstrs((prod_cell[y,'cell',t,'GWh_lfp'] <=  GWh_lfp_kt_li * prod_cath.sum(y,'cath','*','lfp') for y in Y for t in T_cath) ,  name='link_cath_cell_lfp')

# ---- cell ----
link_cell_pack_nmc = m.addConstrs((GWh_bev * prod_pack[y,'pack',t,'bev_nmc'] + GWh_phev * prod_pack[y,'pack',t,'phev_nmc'] <=  prod_cell.sum(y,'cell','*','GWh_nmc') for y in Y for t in T_cell) ,  name='link_cell_pack_nmc')

# ---- cell ----
link_cell_pack_lfp = m.addConstrs((GWh_bev * prod_pack[y,'pack',t,'bev_lfp'] + GWh_phev * prod_pack[y,'pack',t,'phev_lfp'] <=  prod_cell.sum(y,'cell','*','GWh_lfp') for y in Y for t in T_cell) ,  name='link_cell_pack_lfp')

# ---- cell ----
#link_pack_rec_nmc = m.addConstrs((prod_rec[y,'rec',t,'loh'] <=  GWh_bev / (GWh_nmc_kt_li/loh_li) * prod_pack.sum(y,'pack','*','bev_nmc') + GWh_phev / (GWh_nmc_kt_li/loh_li) * prod_pack.sum(y,'pack','*','phev_nmc') for y in Y for t in T_pack) ,  name='link_pack_rec_nmc')

# ---- cell ----
#link_pack_rec_lfp = m.addConstrs((prod_rec[y,'rec',t,'lce'] <=  GWh_bev / (GWh_lfp_kt_li/lce_li) * prod_pack.sum(y,'pack','*','bev_lfp') + GWh_phev / (GWh_lfp_kt_li/lce_li) * prod_pack.sum(y,'pack','*','phev_lfp') for y in Y for t in T_pack) ,  name='link_pack_rec_lfp')

# ---- cell ----
# 25 kt Li / year max
max_cap_mine = 25

# ---- cell ----
#Spod Initial Mines
initial_mine_spod_constr = m.addConstrs((active_mine[y,'mine', 'spod'] == 4 for y in Y_start), name = 'initial_mine_spod_constr')
initial_mine_capacity_spod_constr =m.addConstrs((capacity_mine[y,'mine', 'spod'] == 100 for y in Y_start), name = 'initial_mine_capacity_spod_constr')

# Brine Intial Mines
initial_mine_brine_constr = m.addConstrs((active_mine[y,'mine', 'brine'] == 4 for y in Y_start), name = 'initial_mine_brine_constr')
initial_mine_capacity_brine_constr = m.addConstrs((capacity_mine[y,'mine', 'brine'] == 100 for y in Y_start), name = 'initial_mine_capacity_brine_constr')

# Clay Initial Mines
initial_mine_clay_constr = m.addConstrs((active_mine[y,'mine', 'clay'] == 0 for y in Y_start), name = 'initial_mine_clay_constr')
inital_mine_capacity_clay_constr = m.addConstrs((capacity_mine[y,'mine', 'clay'] == 0 for y in Y_start), name = 'initial_mine_capacity_clay_constr')



# ---- cell ----
#In Construction Variable
# in_construction_mine = m.addVars(YST_mine, lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'in_construction_mine')
# in_construction_mine_constr = m.addConstrs((in_construction_mine[y,'mine', t] == invest_mine[y,'mine', t] + in_construction_mine[(y-1),'mine',t] - (active_mine[(y),'mine',t] - active_mine[(y-1),'mine',t])  for y in Y_warm for t in T_mine) ,  name='in_construction_mine_constr')

#Y_start_minus_construction = [2020, 2021, 2022, 2024]
# #Mines in Construction
# m.addConstrs(in_construction_mine[y,'mine', t] == 0 for y in Y_start_minus_construction for t in T_mine)

# #Mines in Construction
# m.addConstr(in_construction_mine[2023, 'mine', 'clay'] == 1)
# m.addConstr(in_construction_mine[2023, 'mine', 'spod'] == 1)
# m.addConstr(in_construction_mine[2023, 'mine', 'brine'] == 1)


# ---- cell ----
active_mine_constr = m.addConstrs((active_mine[y,'mine', t] == active_mine[(y-1),'mine',t] + invest_mine[(y-5),'mine',t]  for y in Y_warm for t in T_mine) ,  name='active_mine_constr')

# ---- cell ----
invest_mine_constr = m.addConstrs((new_capacity_mine[y,'mine', t] <= max_cap_mine * invest_mine[(y),'mine',t] for y in Y for t in T_mine) ,  name='invest_mine_constr')

# ---- cell ----
new_capacity_mine_constr = m.addConstrs((capacity_mine[y,'mine', t] <= new_capacity_mine[(y-5),'mine',t] + capacity_mine[(y-1),'mine',t] for y in Y_warm for t in T_mine) ,  name='new_capacity_mine_constr')

# ---- cell ----
capacity_mine_constr = m.addConstrs((prod_mine[y,'mine', t] <= capacity_mine[(y),'mine',t] for y in Y for t in T_mine) ,  name='capacity_mine_constr')

# ---- cell ----
max_new_units_mine_constr = m.addConstrs(invest_mine.sum(y,'mine','*') <= max_new_units for y in Y)

# ---- cell ----
# kt Li by weight
resources_brine = 40000
resources_spod = 40000
resources_clay = 20000

# ---- cell ----
resources_brine_constr = m.addConstr((prod_mine.sum('*','mine', 'brine') <= resources_brine) ,  name='resources_brine_constr')
resources_spod_constr = m.addConstr((prod_mine.sum('*','mine', 'spod') <= resources_spod) ,  name='resources_spod_constr')
resources_clay_constr = m.addConstr((prod_mine.sum('*','mine', 'clay') <= resources_brine) ,  name='resources_clay_constr')

# ---- cell ----
# kt of loh or lce
max_cap_proc = 100

# ---- cell ----
#Spod to LOH Initial procs
initial_proc_spod_loh_constr = m.addConstrs((active_proc[y,'proc', 'spod', 'loh'] == 4 for y in Y_start), name = 'initial_proc_spod_loh_constr')
initial_proc_capacity_spod_loh_constr =m.addConstrs((capacity_proc[y,'proc', 'spod', 'loh'] == 400 for y in Y_start), name = 'initial_proc_capacity_spod_loh_constr')
    
# Brine to LCE Intial procs
initial_proc_brine_lce_constr = m.addConstrs((active_proc[y,'proc', 'brine', 'lce'] == 4 for y in Y_start), name = 'initial_proc_brine_lce_constr')
initial_proc_capacity_brine_lce_constr =m.addConstrs((capacity_proc[y,'proc', 'brine', 'lce'] == 400 for y in Y_start), name = 'initial_proc_capacity_brine_lce_constr')


# Setting Zeros
initial_proc_zero_constr = m.addConstrs((active_proc[y,'proc', 'clay', 'lce'] + active_proc[y,'proc', 'clay', 'loh'] + active_proc[y,'proc', 'spod', 'lce'] + active_proc[y,'proc', 'brine', 'loh'] == 0 for y in Y_start), name = 'initial_proc_zero_constr')
inital_proc_capacity_zero_constr = m.addConstrs((capacity_proc[y,'proc', 'clay', 'lce'] + capacity_proc[y,'proc', 'clay', 'loh'] + capacity_proc[y,'proc', 'spod', 'lce'] + capacity_proc[y,'proc', 'brine', 'loh'] == 0 for y in Y_start), name = 'initial_proc_capacity_zero_constr')



# ---- cell ----
active_proc_constr = m.addConstrs((active_proc[y,'proc',i, t] == active_proc[(y-1),'proc', i, t] + invest_proc[(y-5),'proc',i, t]  for y in Y_warm for i in T_mine for t in T_proc) ,  name='active_proc_constr')

# ---- cell ----
invest_proc_constr = m.addConstrs((new_capacity_proc[y,'proc',i, t] <= max_cap_proc * invest_proc[(y),'proc',i,t] for y in Y for i in T_mine for t in T_proc) ,  name='invest_proc_constr')

# ---- cell ----
new_capacity_proc_constr = m.addConstrs((capacity_proc[y,'proc',i, t] <= new_capacity_proc[(y-5),'proc',i,t] + capacity_proc[(y-1),'proc',i,t] for y in Y_warm for i in T_mine for t in T_proc) ,  name='new_capacity_proc_constr')

# ---- cell ----
capacity_proc_constr = m.addConstrs((prod_proc[y,'proc', i,t] <= capacity_proc[(y),'proc',i,t] for y in Y for i in T_mine for t in T_proc) ,  name='capacity_proc_constr')

# ---- cell ----
max_new_units_proc_constr = m.addConstrs(invest_proc.sum(y,'proc','*') <= max_new_units for y in Y)

# ---- cell ----
# kt of cathode active materials
max_cap_cath = 12

# ---- cell ----
#loh to nmc Initial caths
initial_cath_loh_nmc_constr = m.addConstrs((active_cath[y,'cath', 'loh', 'nmc'] == 10 for y in Y_start), name = 'initial_cath_loh_nmc_constr')
initial_cath_capacity_loh_nmc_constr =m.addConstrs((capacity_cath[y,'cath', 'loh', 'nmc'] == 100 for y in Y_start), name = 'initial_cath_capacity_loh_nmc_constr')
    
# lce to lfp Intial caths
initial_cath_lce_lfp_constr = m.addConstrs((active_cath[y,'cath', 'lce', 'lfp'] == 5 for y in Y_start), name = 'initial_cath_lce_lfp_constr')
initial_cath_capacity_lce_lfp_constr =m.addConstrs((capacity_cath[y,'cath', 'lce', 'lfp'] == 50 for y in Y_start), name = 'initial_cath_capacity_lce_lfp_constr')


# Setting Zeros
initial_cath_zero_constr = m.addConstrs((active_cath[y,'cath', 'loh', 'lfp'] + active_cath[y,'cath', 'lce', 'nmc']  == 0 for y in Y_start), name = 'initial_cath_zero_constr')
inital_cath_capacity_zero_constr = m.addConstrs((capacity_cath[y,'cath', 'loh', 'lfp'] + capacity_cath[y,'cath', 'lce', 'nmc'] == 0 for y in Y_start), name = 'initial_cath_capacity_zero_constr')




# ---- cell ----
active_cath_constr = m.addConstrs((active_cath[y,'cath',i, t] == active_cath[(y-1),'cath', i, t] + invest_cath[(y-5),'cath',i, t]  for y in Y_warm for i in T_proc for t in T_cath) ,  name='active_cath_constr')

# ---- cell ----
invest_cath_constr = m.addConstrs((new_capacity_cath[y,'cath',i, t] <= max_cap_cath * invest_cath[(y),'cath',i,t] for y in Y for i in T_proc for t in T_cath) ,  name='invest_cath_constr')

# ---- cell ----
new_capacity_cath_constr = m.addConstrs((capacity_cath[y,'cath',i, t] <= new_capacity_cath[(y-5),'cath',i,t] + capacity_cath[(y-1),'cath',i,t] for y in Y_warm for i in T_proc for t in T_cath) ,  name='new_capacity_cath_constr')

# ---- cell ----
capacity_cath_constr = m.addConstrs((prod_cath[y,'cath', i,t] <= capacity_cath[(y),'cath',i,t] for y in Y for i in T_proc for t in T_cath) ,  name='capacity_cath_constr')

# ---- cell ----
max_new_units_cath_constr = m.addConstrs(invest_cath.sum(y,'cath','*') <= max_new_units for y in Y)

# ---- cell ----
# GWh of cells
max_cap_cell = 100

# ---- cell ----
#nmc to GWh_nmc Initial cells
initial_cell_nmc_GWh_nmc_constr = m.addConstrs((active_cell[y,'cell', 'nmc', 'GWh_nmc'] == 20 for y in Y_start), name = 'initial_cell_nmc_GWh_nmc_constr')
initial_cell_capacity_nmc_GWh_nmc_constr =m.addConstrs((capacity_cell[y,'cell', 'nmc', 'GWh_nmc'] == 1500 for y in Y_start), name = 'initial_cell_capacity_nmc_GWh_nmc_constr')
    
# lfp to GWh_lfp Intial cells
initial_cell_lfp_GWh_lfp_constr = m.addConstrs((active_cell[y,'cell', 'lfp', 'GWh_lfp'] == 10 for y in Y_start), name = 'initial_cell_lfp_GWh_lfp_constr')
initial_cell_capacity_lfp_GWh_lfp_constr =m.addConstrs((capacity_cell[y,'cell', 'lfp', 'GWh_lfp'] == 1000 for y in Y_start), name = 'initial_cell_capacity_lfp_GWh_lfp_constr')


# Setting Zeros
initial_cell_zero_constr = m.addConstrs((active_cell[y,'cell', 'nmc', 'GWh_lfp'] + active_cell[y,'cell', 'lfp', 'GWh_nmc']  == 0 for y in Y_start), name = 'initial_cell_zero_constr')
inital_cell_capacity_zero_constr = m.addConstrs((capacity_cell[y,'cell', 'nmc', 'GWh_lfp'] + capacity_cell[y,'cell', 'lfp', 'GWh_nmc'] == 0 for y in Y_start), name = 'initial_cell_capacity_zero_constr')




# ---- cell ----
active_cell_constr = m.addConstrs((active_cell[y,'cell',i, t] == active_cell[(y-1),'cell', i, t] + invest_cell[(y-5),'cell',i, t]  for y in Y_warm for i in T_cath for t in T_cell) ,  name='active_cell_constr')

# ---- cell ----
invest_cell_constr = m.addConstrs((new_capacity_cell[y,'cell',i, t] <= max_cap_cell * invest_cell[(y),'cell',i,t] for y in Y for i in T_cath for t in T_cell) ,  name='invest_cell_constr')

# ---- cell ----
new_capacity_cell_constr = m.addConstrs((capacity_cell[y,'cell',i, t] <= new_capacity_cell[(y-5),'cell',i,t] + capacity_cell[(y-1),'cell',i,t] for y in Y_warm for i in T_cath for t in T_cell) ,  name='new_capacity_cell_constr')

# ---- cell ----
capacity_cell_constr = m.addConstrs((prod_cell[y,'cell', i,t] <= capacity_cell[(y),'cell',i,t] for y in Y for i in T_cath for t in T_cell) ,  name='capacity_cell_constr')

# ---- cell ----
max_new_units_cell_constr = m.addConstrs(invest_cell.sum(y,'cell','*') <= max_new_units for y in Y)

# ---- cell ----
# MM of EVs BEVs and PHEVs
max_cap_pack = 1

# ---- cell ----
#nmc to bev_nmc Initial packs
initial_pack_GWh_nmc_bev_nmc_constr = m.addConstrs((active_pack[y,'pack', 'GWh_nmc', 'bev_nmc'] == 10 for y in Y_start), name = 'initial_pack_nmc_bev_nmc_constr')
initial_pack_capacity_GWh_nmc_bev_nmc_constr =m.addConstrs((capacity_pack[y,'pack', 'GWh_nmc', 'bev_nmc'] == 10 for y in Y_start), name = 'initial_pack_capacity_nmc_bev_nmc_constr')
    
# lfp to bev_lfp Intial packs
initial_pack_GWh_lfp_bev_lfp_constr = m.addConstrs((active_pack[y,'pack', 'GWh_lfp', 'bev_lfp'] == 5 for y in Y_start), name = 'initial_pack_lfp_bev_lfp_constr')
initial_pack_capacity_GWh_lfp_bev_lfp_constr =m.addConstrs((capacity_pack[y,'pack', 'GWh_lfp', 'bev_lfp'] == 5 for y in Y_start), name = 'initial_pack_capacity_lfp_bev_lfp_constr')

#nmc to phev_nmc Initial packs
initial_pack_GWh_nmc_phev_nmc_constr = m.addConstrs((active_pack[y,'pack', 'GWh_nmc', 'phev_nmc'] == 5 for y in Y_start), name = 'initial_pack_nmc_phev_nmc_constr')
initial_pack_capacity_GWh_nmc_phev_nmc_constr =m.addConstrs((capacity_pack[y,'pack', 'GWh_nmc', 'phev_nmc'] == 5 for y in Y_start), name = 'initial_pack_capacity_nmc_phev_nmc_constr')
    
# lfp to phev_lfp Intial packs
initial_pack_GWh_lfp_phev_lfp_constr = m.addConstrs((active_pack[y,'pack', 'GWh_lfp', 'phev_lfp'] == 2 for y in Y_start), name = 'initial_pack_lfp_phev_lfp_constr')
initial_pack_capacity_GWh_lfp_phev_lfp_constr =m.addConstrs((capacity_pack[y,'pack', 'GWh_lfp', 'phev_lfp'] == 2 for y in Y_start), name = 'initial_pack_capacity_lfp_phev_lfp_constr')


# Setting Zeros
initial_pack_zero_constr = m.addConstrs((active_pack[y,'pack', 'GWh_nmc', 'bev_lfp'] + active_pack[y,'pack', 'GWh_lfp', 'bev_nmc'] + active_pack[y,'pack', 'GWh_nmc', 'phev_lfp'] + active_pack[y,'pack', 'GWh_lfp', 'phev_nmc']  == 0 for y in Y_start), name = 'initial_pack_zero_constr')
inital_pack_capacity_zero_constr = m.addConstrs((capacity_pack[y,'pack', 'GWh_nmc', 'bev_lfp'] + capacity_pack[y,'pack', 'GWh_lfp', 'bev_nmc'] + capacity_pack[y,'pack', 'GWh_nmc', 'phev_lfp'] + capacity_pack[y,'pack', 'GWh_lfp', 'phev_nmc'] == 0 for y in Y_start), name = 'initial_pack_capacity_zero_constr')

# ---- cell ----
active_pack_constr = m.addConstrs((active_pack[y,'pack',i, t] == active_pack[(y-1),'pack', i, t] + invest_pack[(y-5),'pack',i, t]  for y in Y_warm for i in T_cell for t in T_pack) ,  name='active_pack_constr')

# ---- cell ----
invest_pack_constr = m.addConstrs((new_capacity_pack[y,'pack',i, t] <= max_cap_pack * invest_pack[(y),'pack',i,t] for y in Y for i in T_cell for t in T_pack) ,  name='invest_pack_constr')

# ---- cell ----
new_capacity_pack_constr = m.addConstrs((capacity_pack[y,'pack',i, t] <= new_capacity_pack[(y-5),'pack',i,t] + capacity_pack[(y-1),'pack',i,t] for y in Y_warm for i in T_cell for t in T_pack) ,  name='new_capacity_pack_constr')

# ---- cell ----
capacity_pack_constr = m.addConstrs((prod_pack[y,'pack', i,t] <= capacity_pack[(y),'pack',i,t] for y in Y for i in T_cell for t in T_pack) ,  name='capacity_pack_constr')

# ---- cell ----
max_new_units_pack_constr = m.addConstrs(invest_pack.sum(y,'pack','*') <= max_new_units for y in Y)

# ---- cell ----
# kt of LCE and LOH
max_cap_rec = 15

# ---- cell ----
# Setting Zeros
initial_rec_zero_constr = m.addConstrs((active_rec[y,'rec', 'bev_nmc', 'lce'] + active_rec[y,'rec', 'bev_lfp', 'loh'] + active_rec[y,'rec', 'bev_nmc', 'loh'] + active_rec[y,'rec', 'bev_lfp', 'lce'] +
                                        active_rec[y,'rec', 'phev_nmc', 'lce'] + active_rec[y,'rec', 'phev_lfp', 'loh'] + active_rec[y,'rec', 'phev_nmc', 'loh'] + active_rec[y,'rec', 'phev_lfp', 'lce']  == 0 for y in Y_start), name = 'initial_rec_zero_constr')

initial_rec_capacity_zero_constr = m.addConstrs((capacity_rec[y,'rec', 'bev_nmc', 'lce'] + capacity_rec[y,'rec', 'bev_lfp', 'loh'] + capacity_rec[y,'rec', 'bev_nmc', 'loh'] + capacity_rec[y,'rec', 'bev_lfp', 'lce'] +
                                        capacity_rec[y,'rec', 'phev_nmc', 'lce'] + capacity_rec[y,'rec', 'phev_lfp', 'loh'] + capacity_rec[y,'rec', 'phev_nmc', 'loh'] + capacity_rec[y,'rec', 'phev_lfp', 'lce']  == 0 for y in Y_start), name = 'initial_rec_capacity_zero_constr')

# ---- cell ----
active_rec_constr = m.addConstrs((active_rec[y,'rec',i, t] == active_rec[(y-1),'rec', i, t] + invest_rec[(y-5),'rec',i, t]  for y in Y_warm for i in T_pack for t in T_rec) ,  name='active_rec_constr')

# ---- cell ----
invest_rec_constr = m.addConstrs((new_capacity_rec[y,'rec',i, t] <= max_cap_rec * invest_rec[(y),'rec',i,t] for y in Y for i in T_pack for t in T_rec) ,  name='invest_rec_constr')

# ---- cell ----
new_capacity_rec_constr = m.addConstrs((capacity_rec[y,'rec',i, t] <= new_capacity_rec[(y-5),'rec',i,t] + capacity_rec[(y-1),'rec',i,t] for y in Y_warm for i in T_pack for t in T_rec) ,  name='new_capacity_rec_constr')

# ---- cell ----
capacity_rec_constr = m.addConstrs((prod_rec[y,'rec', i,t] <= capacity_rec[(y),'rec',i,t] for y in Y for i in T_pack for t in T_rec) ,  name='capacity_rec_constr')

# ---- cell ----
max_new_units_rec_constr = m.addConstrs(invest_rec.sum(y,'rec','*') <= max_new_units for y in Y)

# ---- cell ----
mine_cost = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'mine_cost')
mine_cost_constr = m.addConstr(mine_cost == prod_mine.prod(mine_prod_cost) + new_capacity_mine.prod(mine_var_cost) + invest_mine.prod(mine_fixed_cost),  name='mine_cost_constr')

# ---- cell ----
proc_cost = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'proc_cost')
proc_cost_constr = m.addConstr(proc_cost == prod_proc.prod(proc_prod_cost) + new_capacity_proc.prod(proc_var_cost) + invest_proc.prod(proc_fixed_cost),  name='proc_cost_constr')

# ---- cell ----
cath_cost = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'cath_cost')
cath_cost_constr = m.addConstr(cath_cost == prod_cath.prod(cath_prod_cost) + new_capacity_cath.prod(cath_var_cost) + invest_cath.prod(cath_fixed_cost),  name='cath_cost_constr')

# ---- cell ----
cell_cost = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'cell_cost')
cell_cost_constr = m.addConstr(cell_cost == prod_cell.prod(cell_prod_cost) + new_capacity_cell.prod(cell_var_cost) + invest_cell.prod(cell_fixed_cost),  name='cell_cost_constr')

# ---- cell ----
pack_cost = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'pack_cost')
pack_cost_constr = m.addConstr(pack_cost == prod_pack.prod(pack_prod_cost) + new_capacity_pack.prod(pack_var_cost) + invest_pack.prod(pack_fixed_cost),  name='pack_cost_constr')

# ---- cell ----
rec_cost = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'rec_cost')
rec_cost_constr = m.addConstr(rec_cost == prod_rec.prod(rec_prod_cost) + new_capacity_rec.prod(rec_var_cost) + invest_rec.prod(rec_fixed_cost),  name='rec_cost_constr')

# ---- cell ----
total_cost = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'total_cost')
total_cost_constr = m.addConstr(total_cost == mine_cost+ proc_cost+ cath_cost+ cell_cost+ pack_cost+ rec_cost,  name='total_cost_constr')

# ---- cell ----
mine_CO2 = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'mine_CO2')
mine_CO2_constr = m.addConstr(mine_CO2 == prod_mine.prod(mine_prod_CO2) + new_capacity_mine.prod(mine_var_CO2) + invest_mine.prod(mine_fixed_CO2),  name='mine_CO2_constr')

# ---- cell ----
proc_CO2 = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'proc_CO2')
proc_CO2_constr = m.addConstr(proc_CO2 == prod_proc.prod(proc_prod_CO2) + new_capacity_proc.prod(proc_var_CO2) + invest_proc.prod(proc_fixed_CO2),  name='proc_CO2_constr')

# ---- cell ----
cath_CO2 = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'cath_CO2')
cath_CO2_constr = m.addConstr(cath_CO2 == prod_cath.prod(cath_prod_CO2) + new_capacity_cath.prod(cath_var_CO2) + invest_cath.prod(cath_fixed_CO2),  name='cath_CO2_constr')

# ---- cell ----
cell_CO2 = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'cell_CO2')
cell_CO2_constr = m.addConstr(cell_CO2 == prod_cell.prod(cell_prod_CO2) + new_capacity_cell.prod(cell_var_CO2) + invest_cell.prod(cell_fixed_CO2),  name='cell_CO2_constr')

# ---- cell ----
pack_CO2 = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'pack_CO2')
pack_CO2_constr = m.addConstr(pack_CO2 == prod_pack.prod(pack_prod_CO2) + new_capacity_pack.prod(pack_var_CO2) + invest_pack.prod(pack_fixed_CO2),  name='pack_CO2_constr')

# ---- cell ----
rec_CO2 = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'rec_CO2')
rec_CO2_constr = m.addConstr(rec_CO2 == prod_rec.prod(rec_prod_CO2) + new_capacity_rec.prod(rec_var_CO2) + invest_rec.prod(rec_fixed_CO2),  name='rec_CO2_constr')

# ---- cell ----
total_CO2 = m.addVar(lb = 0, ub = GRB.INFINITY, vtype = GRB.CONTINUOUS, name = 'total_CO2')
total_CO2_constr = m.addConstr(total_CO2 == mine_CO2+ proc_CO2+ cath_CO2+ cell_CO2+ pack_CO2+ rec_CO2,  name='total_CO2_constr')

# ---- cell ----
# Objective: minimize total cost
#m.setObjective(prod_mine.prod(mine_prod_cost)+prod_proc.prod(proc_prod_cost)+prod_cath.prod(cath_prod_cost)+prod_cell.prod(cell_prod_cost)+prod_pack.prod(pack_prod_cost)+prod_rec.prod(rec_prod_cost)+
#               new_capacity_mine.prod(mine_var_cost)+new_capacity_proc.prod(proc_var_cost)+new_capacity_cath.prod(cath_var_cost)+new_capacity_cell.prod(cell_var_cost)+new_capacity_pack.prod(pack_var_cost)+new_capacity_rec.prod(rec_var_cost)+
#               invest_mine.prod(mine_fixed_cost) + invest_proc.prod(proc_fixed_cost) + invest_cath.prod(cath_fixed_cost) + invest_cell.prod(cell_fixed_cost)+invest_pack.prod(pack_fixed_cost)+invest_rec.prod(rec_fixed_cost)
#               ,GRB.MINIMIZE)

# ---- cell ----
m.setObjective(total_cost, GRB.MINIMIZE)

# ---- cell ----
# Save Model File
m.write(str(RESULTS_DIR / 'model.mps'))
# Save Model File
m.write(str(RESULTS_DIR / 'model.lp'))

# ---- cell ----
# TimeLimit in Seconds
m.Params.TimeLimit = 3600
# Node Limit
# m.Params.NodeLimit = 10

# ---- cell ----
# Read Previous Solution
m.read(str(DATA_DIR / 'warm_start.sol'))
#Run optimization engine
m.optimize()

# ---- cell ----
#print(m.ObjVal)
m.ObjVal

# ---- cell ----
print('Total Mine Cost: $ (MM)',f"{mine_cost.X:,.0f}")
print('Total Proc Cost: $ (MM)',f"{proc_cost.X:,.0f}")
print('Total Cath Cost: $ (MM)',f"{cath_cost.X:,.0f}")
print('Total Cell Cost: $ (MM)',f"{cell_cost.X:,.0f}")
print('Total Pack Cost: $ (MM)',f"{pack_cost.X:,.0f}")
print('Total Recycle Cost: $ (MM)',f"{rec_cost.X:,.0f}")
print('Total Cost: $ (MM)',f"{total_cost.X:,.0f}")



# ---- cell ----
print('Total Mine CO2: $ (kt)',f"{mine_CO2.X:,.0f}")
print('Total Proc CO2: $ (kt)',f"{proc_CO2.X:,.0f}")
print('Total Cath CO2: $ (kt)',f"{cath_CO2.X:,.0f}")
print('Total Cell CO2: $ (kt)',f"{cell_CO2.X:,.0f}")
print('Total Pack CO2: $ (kt)',f"{pack_CO2.X:,.0f}")
print('Total Recycle CO2: $ (kt)',f"{rec_CO2.X:,.0f}")
print('Total CO2: $ (kt)',f"{total_CO2.X:,.0f}")


# ---- cell ----
print('Total Cell Cost: $ (MM)',f"{cell_cost.X:,.0f}")

# ---- cell ----
# Variable info

varInfo = [(v.varName, v.X, v.LB, v.UB) for v in m.getVars() ]

df = pd.DataFrame(varInfo)

df.columns=['Variable Name','Solution Value', 'LB','UB']

df.to_excel(str(RESULTS_DIR / "variables.xlsx"), index=False)


df_var = df.query('`Solution Value` > 0')

df_var

# ---- cell ----
# Constraint info

constrInfo = [(c.constrName, m.getRow(c),m.getRow(c).getValue(), c.Sense, c.RHS) for c in m.getConstrs() ]

df = pd.DataFrame(constrInfo)

df.columns=['Constraint Name','Constraint equation', 'Value','Sense','RHS']

df.to_excel(str(RESULTS_DIR / "constraints.xlsx"), index=False)

df

# ---- cell ----
# Save Model Solution
m.write(str(RESULTS_DIR / 'solution.sol'))

# ---- cell ----
# Getting Rid of Model for Reruns
#m.dispose()

# ---- cell ----
# m = gp.read('model.mps', env=env)
# m.read(str(DATA_DIR / 'warm_start.sol'))
# m.optimize()


# ---- cell ----
# start_soln = m.getAttr(GRB.Attr.Start)
# final_soln = m.getAttr(GRB.Attr.Xn)
# diff_btwn_soln = [a - b for a, b in zip(start_soln, final_soln)]
# diff_btwn_soln

# ---- cell ----
print('Code Chunk Run Complete')