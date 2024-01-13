from amaranth import *
from amaranth.lib.wiring import Component, In, Out

__all__ = [
    'Buffer',
]

class Buffer(Component):
    def __init__(self, stream_signature):
        super().__init__({
            'input': In(stream_signature),
            'output': Out(stream_signature),
        })

    def elaborate(self, platform):
        m = Module()

        with m.If(self.output.valid & self.output.ready):
            m.d.sync += self.output.valid.eq(0)
        
        with m.If(~self.output.valid | self.output.ready):
            m.d.comb += self.input.ready.eq(1)

            with m.If(self.input.valid):
                m.d.sync += self.output.valid.eq(1)
                m.d.sync += self.output.wrap().eq(self.input.wrap())

        return m
