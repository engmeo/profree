"""Heterogeneous fleet -> inbound material ledger adapter for response_v2.

Prototype coupling, not physical robotic control. 'delivery time' is a synthetic
scheduler unit and must be calibrated before any operational use.
"""
from copy import deepcopy
from .fleet import scenario

def apply_fleet_arrival(material_spec, fleet_result, quantity=None):
    result=deepcopy(material_spec)
    gate=fleet_result['material_gate']
    arrival=gate['earliest_arrival_after_failure']
    if arrival is None:raise ValueError('no safe robot delivery: demand escalation required')
    if not isinstance(arrival,int) or arrival<0:raise ValueError('invalid fleet ETA')
    name=gate['material']
    demand=sum(int(parts.get(name,0)) for parts in result.get('bom',{}).values())
    qty=demand if quantity is None else quantity
    if not isinstance(qty,int) or qty<=0:raise ValueError('invalid inbound quantity')
    if result.get('initial',{}).get(name,0):
        raise ValueError('bridge requires known inbound material shortage; no silent stock mutation')
    if any(d['material']==name for d in result.get('deliveries',[])):
        raise ValueError('existing delivery for material: explicit merge is required')
    result.setdefault('deliveries',[]).append({'material':name,'time':arrival,'quantity':qty})
    result['source']='SYNTHETIC_FLEET_BRIDGE'
    return result

def example():
    s=scenario()
    material={'initial':{'MAT_A':0},'bom':{'0:0':{'MAT_A':2},'0:1':{'MAT_A':1}},'deliveries':[]}
    return {'fleet':s,'material_for_cpsat':apply_fleet_arrival(material,s)}
if __name__=='__main__':
    import json
    print(json.dumps(example(),indent=2))
