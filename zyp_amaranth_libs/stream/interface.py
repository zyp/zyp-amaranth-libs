from amaranth import *
from amaranth.lib.wiring import Signature, In, Out, PureInterface, connect

import itertools

__all__ = [
    'StreamInterface',
    'MultilaneStreamInterface',
    'StreamSignature',
    'cross_connect',
    'connect_pipeline',
]

class StreamInterface(PureInterface):
    def __init__(self, signature, *, path, src_loc_at = 0):
        super().__init__(signature, path = path, src_loc_at = src_loc_at + 1)

        if signature.backpressure == False:
            self.ready = C(1)

    def wrap(self):
        signals = [self.data]

        if 'first' in self.signature.members:
            signals.append(self.first)

        if 'last' in self.signature.members:
            signals.append(self.last)

        return Cat(signals)

    async def recv(self, sim):
        await self.ready.set(1)
        await sim.tick().until(self.valid)
        
        value = await self.data.get()

        await sim.tick()
        await self.ready.set(0)

        return value

    async def send(self, sim, value):
        await self.data.set(value)

        await self.valid.set(1)
        await sim.tick().until(self.ready)

        await sim.tick()
        await self.valid.set(0)

class MultilaneStreamInterface(PureInterface):
    def __init__(self, signature, *, path, src_loc_at = 0):
        super().__init__(signature, path = path, src_loc_at = src_loc_at + 1)

        if signature.backpressure == False:
            self.ready = C(1)

    def wrap(self):
        signals = [self.data]

        if 'first' in self.signature.members:
            signals.append(self.first)

        if 'last' in self.signature.members:
            signals.append(self.last)

        return Cat(signals)

    async def recv_packet(self, sim):
        assert 'last' in self.signature.members

        await self.ready.set(1)

        values = []
        done = False

        while not done:
            await sim.tick().until(self.valid)

            for i in range(self.signature.lanes):
                values.append(await self.data[i].get())

                if await self.last[i].get():
                    done = True
                    break

            if not done:
                await sim.tick()

        await self.ready.set(0)

        return values

    async def send_packet(self, sim, values):
        transactions = list(itertools.batched(values, self.signature.lanes))
        first = 0
        last = len(transactions) - 1

        for transaction_num, data in enumerate(transactions):
            await sim.delay(1e-12)
            await self.valid.set(1)
            for i, value in enumerate(data):
                await self.data[i].set(value)

                if 'first' in self.signature.members:
                    await self.first[i].set(transaction_num == first and i == 0)
                if 'last' in self.signature.members:
                    await self.last[i].set(transaction_num == last and i == len(data) - 1)

            await sim.tick().until(self.ready)
            await sim.tick()
        
        await self.valid.set(0)

class StreamSignature(Signature):
    def __init__(self, data_shape, *, backpressure = True, first = False, last = False, lanes = None):
        members = {
            'data': Out(data_shape),
            'valid': Out(1),
            'ready': In(1),
        }

        if first:
            members['first'] = Out(1)

        if last:
            members['last'] = Out(1)

        if lanes is not None:
            for name in ['data', 'first', 'last']:
                if name in members:
                    members[name] = members[name].array(lanes)

        super().__init__(members)

        self.backpressure = backpressure
        self.lanes = lanes

    def create(self, *, path = (), src_loc_at = 0):
        if self.lanes is None:
            return StreamInterface(self, path = path, src_loc_at = src_loc_at + 1)
        else:
            return MultilaneStreamInterface(self, path = path, src_loc_at = src_loc_at + 1)

def cross_connect(m, left, right):
    assert 'input' in left.signature.members
    assert 'output' in left.signature.members
    assert 'input' in right.signature.members
    assert 'output' in right.signature.members

    connect(m, left.input, right.output)
    connect(m, left.output, right.input)

class _OutputInterface:
    def __init__(self, output):
        self.output = output
        self.signature = Signature({'output': Out(output.signature)})

class _InputInterface:
    def __init__(self, input):
        self.input = input
        self.signature = Signature({'input': Out(input.signature)})

def connect_pipeline(m, *interfaces):
    interfaces = list(interfaces)

    if not 'output' in interfaces[0].signature.members:
        interfaces[0] = _OutputInterface(interfaces[0])

    if not 'input' in interfaces[-1].signature.members:
        interfaces[-1] = _InputInterface(interfaces[-1])

    for source, sink in itertools.pairwise(interfaces):
        assert 'output' in source.signature.members
        assert 'input' in sink.signature.members

        connect(m, source.output, sink.input)
