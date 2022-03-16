from typing import Dict, List

from muse_gui.data_defs.commodity import Commodity

from .base import BaseBackDependents, BaseDatastore, BaseForwardDependents
from muse_gui.data_defs.region import Region
from .exceptions import KeyAlreadyExists, KeyNotFound
from dataclasses import dataclass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Datastore

@dataclass
class RegionBackDependents(BaseBackDependents):
    pass

@dataclass
class RegionForwardDependents(BaseForwardDependents):
    commodities: List[str]
    processes: List[str]
    agents: List[str]

class RegionDatastore(BaseDatastore[Region, RegionBackDependents, RegionForwardDependents]):
    _regions: Dict[str, Region]
    def __init__(self, parent: "Datastore", regions: List[Region] = []) -> None:
        self._parent = parent
        self._regions = {}
        for region in regions:
            self.create(region)


    def create(self, model: Region) -> Region:
        if model.name in self._regions:
            raise KeyAlreadyExists(model.name, self)
        else:
            self._regions[model.name] = model
            return model
    def update(self, key: str, model: Region) -> Region:
        if key not in self._regions:
            raise KeyNotFound(key, self)
        else:
            self._regions[key] = model
            return model
    def read(self, key: str) -> Region:
        if key not in self._regions:
            raise KeyNotFound(key, self)
        else:
            return self._regions[key]

    def delete(self, key: str) -> None:
        existing = self.read(key)
        forward_deps = self.forward_dependents(existing)
        for commodity_key in forward_deps.commodities:
            try:
                self._parent.commodity.delete(commodity_key)
            except KeyNotFound:
                pass
        for process_key in forward_deps.processes:
            try:
                self._parent.process.delete(process_key)
            except KeyNotFound:
                pass
        for agent_key in forward_deps.agents:
            try:
                self._parent.agent.delete(agent_key)
            except KeyNotFound:
                pass
        self._regions.pop(key)
        return None
    
    def back_dependents(self, model: Region) -> RegionBackDependents:
        return RegionBackDependents()

    def forward_dependents(self, model: Region) -> RegionForwardDependents:
        commodities = []
        for key, commodity in self._parent.commodity._commodities.items():
            for price in commodity.commodity_prices.prices:
                if price.region_name == model.name:
                    commodities.append(key)
        processes = []
        for key, process in self._parent.process._processes.items():
            if process.region == model.name:
                processes.append(key)
        agents = []
        for key, agent in self._parent.agent._agents.items():
            if agent.region == model.name:
                agents.append(key)
        return RegionForwardDependents(
            commodities = commodities, 
            processes= processes,
            agents = agents
        )
