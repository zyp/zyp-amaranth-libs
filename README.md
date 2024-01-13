zyp's Amaranth libraries
========================

This is a collection of various useful stuff I've made while working on [Amaranth](https://amaranth-lang.org/) based projects.

API stability is not guaranteed. Linking to a specific git revision is recommended.

Streams
-------
The `stream` library contains building blocks for working with stream interfaces.

Once a stream library gets accepted into Amaranth itself, expect this library to be supplanted.

Note: The simulation helper methods on the interface objects are utilizing features from the currently not yet accepted [Amaranth RFC #36](https://github.com/amaranth-lang/rfcs/pull/36) and will not work with mainline Amaranth until it is accepted and an implementation is merged.

Simulation platform
-------------------
The `sim_platform` library contains a simulation platform with simulated IO registers.

Note: This library is utilizing features from the currently not yet accepted [Amaranth RFC #36](https://github.com/amaranth-lang/rfcs/pull/36) and will not work with mainline Amaranth until it is accepted and an implementation is merged.
