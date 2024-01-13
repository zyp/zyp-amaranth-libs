from amaranth.build.res import ResourceManager

__all__ = [
    'SimPlatform',
]

class SimPort:
    def __init__(self, sim, pin, port, attrs, invert):
        self.pin = pin
        self.port = port
        self.attrs = attrs
        self.invert = (2 << len(port)) - 1 if invert else 0

        if pin.xdr == 0:
            if 'i' in pin.dir:
                sim.add_process(self.in_xdr0, passive = True)
            if 'o' in pin.dir:
                sim.add_process(self.out_xdr0, passive = True)

        elif pin.xdr == 1:
            if 'i' in pin.dir:
                sim.add_process(self.in_xdr1, passive = True)
            if 'o' in pin.dir:
                sim.add_process(self.out_xdr1, passive = True)

        elif pin.xdr == 2:
            if 'i' in pin.dir:
                sim.add_process(self.in_xdr2, passive = True)
            if 'o' in pin.dir:
                sim.add_process(self.out_xdr2, passive = True)

    async def in_xdr0(self, sim):
        while True:
            await sim.changed(self.port.io)
            value = await self.port.io.get()
            await self.pin.i.set(value ^ self.invert)

    async def out_xdr0(self, sim):
        while True:
            await sim.changed(self.pin.o)
            value = await self.pin.o.get()
            await self.port.io.set(value ^ self.invert)

    async def in_xdr1(self, sim):
        while True:
            await sim.changed(self.pin.i_clk, 1)
            value = await self.port.io.get()
            await self.pin.i.set(value ^ self.invert)

    async def out_xdr1(self, sim):
        while True:
            await sim.changed(self.pin.o_clk, 1)
            value = await self.pin.o.get()
            await self.port.io.set(value ^ self.invert)

    async def in_xdr2(self, sim):
        d0 = 0
        d1 = 0
        while True:
            await sim.changed(self.pin.i_clk, 1)
            value, d0 = d0, await self.port.io.get()
            await self.pin.i0.set(value ^ self.invert)
            await self.pin.i1.set(d1 ^ self.invert)
            await sim.changed(self.pin.i_clk, 0)
            d1 = await self.port.io.get()

    async def out_xdr2(self, sim):
        d0 = (0, 0)
        d1 = (0, 0)
        while True:
            await sim.changed(self.pin.o_clk, 1)
            value, *d0 = *d0, await self.pin.o0.get()
            await self.port.io.set(value ^ self.invert)
            value, *d1 = *d1, await self.pin.o1.get()
            await sim.changed(self.pin.o_clk, 0)
            await self.port.io.set(value ^ self.invert)

class SimPlatform(ResourceManager):
    def prepare(self, sim):
        for pin, port, attrs, invert in self.iter_single_ended_pins():
            SimPort(sim, pin, port, attrs, invert)
