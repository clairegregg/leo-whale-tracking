# Low-Earth Orbit Satellites for Whale Tracking
This was completed for the final project of Scalable Computing CS7NS1, to model a use-case for LEO (low earth orbit) satellites.

## Instructions for Use

Set up satellites using https://github.com/Scalable-2024/bobb, then run whales.py with any number of whales to simulate the use case.

## Use Case

We are modelling the use case of using LEO satellites to help track whales/sharks. The basic idea here is to attach a waterproof LEO antenna to a whale, which can connect to the satellites when the whale breaches (comes above the water), or when they feed close to the surface. A small processor on the whale can collect data from sensors at all times, and whenever the whale comes close to the surface, it can attempt to connect to a LEO satellite as fast as possible, and send as much data as possible.

We can take for example the Humpback Whale - per Heide-Jørgensen et al., it is at the surface (<=2m from the surface of the water) around 25-30% of the time [1]. This can be used to model an interesting use case for LEO satellites with the following problems introduced:
1. Initial connection time cannot be predicted at all.
2. Connections sending data may be cut off suddenly at any point.
3. More noise may be introduced because of water.


[1] Heide-Jørgensen, M.P. and Laidre, K.L. (2023). Surfacing time, availability bias and abundance of humpback whales in West Greenland. IWC Journal of Cetacean Research and Management, 15(1), pp.1–8. doi:https://doi.org/10.47536/jcrm.v15i1.510.

‌
