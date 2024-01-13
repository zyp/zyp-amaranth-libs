import migen

from litex.build import io

from amaranth.lib import wiring

class PadsProxy:
    def __init__(self, glue, name, migen_pads, dir, xdr):
        signature_members = {}

        if isinstance(migen_pads, migen.Record):
            if dir is None:
                dir = {}
            elif isinstance(dir, str):
                dir = {subname: dir for subname, *_ in migen_pads.layout}

            if xdr is None:
                xdr = {}
            elif isinstance(xdr, int):
                xdr = {subname: xdr for subname, *_ in migen_pads.layout}

            assert isinstance(dir, dict) or isinstance(dir, str)
            assert isinstance(xdr, dict)

            for subname, *_ in migen_pads.layout:
                subsignal = PadsProxy(glue, f'{name}_{subname}', getattr(migen_pads, subname), dir.get(subname), xdr.get(subname))
                setattr(self, subname, subsignal)
                signature_members[subname] = wiring.Out(subsignal.signature)

        elif isinstance(migen_pads, migen.Signal):
            if dir is None:
                dir = '-'
            if xdr is None:
                xdr = 0
            
            invert = getattr(migen_pads, 'inverted', False)

            if dir == '-':
                pass

            elif xdr == 0:
                if dir == 'i':
                    self.i = glue.from_migen(migen_pads, name = f'{name}_i', invert = invert)
                    signature_members['i'] = wiring.Out(self.i.shape())
                elif dir == 'o':
                    self.o = glue.from_migen(migen_pads, name = f'{name}_o', invert = invert)
                    signature_members['o'] = wiring.In(self.o.shape())
                elif dir == 'io':
                    i = migen.Signal.like(migen_pads)
                    o = migen.Signal.like(migen_pads)
                    oe = migen.Signal()
                    glue.specials += io.Tristate(migen_pads, o, migen.Replicate(oe, migen_pads.nbits), i)
                    self.i = glue.from_migen(i, name = f'{name}_i', invert = invert)
                    signature_members['i'] = wiring.Out(self.i.shape())
                    self.o = glue.from_migen(o, name = f'{name}_o', invert = invert)
                    signature_members['o'] = wiring.In(self.o.shape())
                    self.oe = glue.from_migen(oe, name = f'{name}_oe')
                    signature_members['oe'] = wiring.In(self.oe.shape())
                elif dir == 'oe':
                    i = migen.Signal.like(migen_pads)
                    o = migen.Signal.like(migen_pads)
                    oe = migen.Signal()
                    glue.specials += io.Tristate(migen_pads, i = i, o = o, oe = migen.Replicate(oe, migen_pads.nbits))
                    self.o = glue.from_migen(o, name = f'{name}_o', invert = invert)
                    signature_members['o'] = wiring.In(self.o.shape())
                    self.oe = glue.from_migen(oe, name = f'{name}_oe')
                    signature_members['oe'] = wiring.In(self.oe.shape())
                else:
                    raise RuntimeError(f'{xdr=} and {dir=} not supported yet')

            elif xdr == 1:
                if dir == 'i':
                    i = migen.Signal.like(migen_pads)
                    i_clk = migen.Signal()
                    for idx in range(migen_pads.nbits):
                        glue.specials += io.SDRInput(i = migen_pads[idx], o = i[idx], clk = i_clk)
                    self.i = glue.from_migen(i, name = f'{name}_i', invert = invert)
                    signature_members['i'] = wiring.Out(self.i.shape())
                    self.i_clk = glue.from_migen(i_clk, name = f'{name}_i_clk')
                    signature_members['i_clk'] = wiring.In(self.i_clk.shape())
                elif dir == 'o':
                    o = migen.Signal.like(migen_pads)
                    o_clk = migen.Signal()
                    for idx in range(migen_pads.nbits):
                        glue.specials += io.SDROutput(i = o[idx], o = migen_pads[idx], clk = o_clk)
                    self.o = glue.from_migen(o, name = f'{name}_o', invert = invert)
                    signature_members['o'] = wiring.In(self.o.shape())
                    self.o_clk = glue.from_migen(o_clk, name = f'{name}_o_clk')
                    signature_members['o_clk'] = wiring.In(self.o_clk.shape())
                elif dir == 'io':
                    i = migen.Signal.like(migen_pads)
                    _i = migen.Signal.like(migen_pads)
                    o = migen.Signal.like(migen_pads)
                    _o = migen.Signal.like(migen_pads)
                    oe = migen.Signal()
                    i_clk = migen.Signal()
                    o_clk = migen.Signal()
                    glue.specials += io.Tristate(migen_pads, i = _i, o = _o, oe = migen.Replicate(oe, migen_pads.nbits))
                    for idx in range(migen_pads.nbits):
                        glue.specials += io.SDRInput(i = _i[idx], o = i[idx], clk = i_clk)
                        glue.specials += io.SDROutput(i = o[idx], o = _o[idx], clk = o_clk)
                    self.i = glue.from_migen(i, name = f'{name}_i', invert = invert)
                    signature_members['i'] = wiring.Out(self.i.shape())
                    self.o = glue.from_migen(o, name = f'{name}_o', invert = invert)
                    signature_members['o'] = wiring.In(self.o.shape())
                    self.oe = glue.from_migen(oe, name = f'{name}_oe')
                    signature_members['oe'] = wiring.In(self.oe.shape())
                    self.i_clk = glue.from_migen(i_clk, name = f'{name}_i_clk')
                    signature_members['i_clk'] = wiring.In(self.i_clk.shape())
                    self.o_clk = glue.from_migen(o_clk, name = f'{name}_o_clk')
                    signature_members['o_clk'] = wiring.In(self.o_clk.shape())
                elif dir == 'oe':
                    _i = migen.Signal.like(migen_pads)
                    o = migen.Signal.like(migen_pads)
                    _o = migen.Signal.like(migen_pads)
                    oe = migen.Signal()
                    o_clk = migen.Signal()
                    glue.specials += io.Tristate(migen_pads, i = _i, o = _o, oe = migen.Replicate(oe, migen_pads.nbits))
                    for idx in range(migen_pads.nbits):
                        glue.specials += io.SDROutput(i = o[idx], o = _o[idx], clk = o_clk)
                    self.o = glue.from_migen(o, name = f'{name}_o', invert = invert)
                    signature_members['o'] = wiring.In(self.o.shape())
                    self.oe = glue.from_migen(oe, name = f'{name}_oe')
                    signature_members['oe'] = wiring.In(self.oe.shape())
                    self.o_clk = glue.from_migen(o_clk, name = f'{name}_o_clk')
                    signature_members['o_clk'] = wiring.In(self.o_clk.shape())
                else:
                    raise RuntimeError(f'{xdr=} and {dir=} not supported yet')

            elif xdr == 2:
                if dir == 'i':
                    i0 = migen.Signal.like(migen_pads)
                    i1 = migen.Signal.like(migen_pads)
                    i_clk = migen.Signal()
                    for idx in range(migen_pads.nbits):
                        glue.specials += io.DDRInput(i = migen_pads[idx], o1 = i0[idx], o2 = i1[idx], clk = i_clk)
                    self.i0 = glue.from_migen(i0, name = f'{name}_i0', invert = invert)
                    self.i1 = glue.from_migen(i1, name = f'{name}_i1', invert = invert)
                    signature_members['i0'] = wiring.Out(self.i0.shape())
                    signature_members['i1'] = wiring.Out(self.i1.shape())
                    self.i_clk = glue.from_migen(i_clk, name = f'{name}_i_clk')
                    signature_members['i_clk'] = wiring.In(self.i_clk.shape())
                elif dir == 'o':
                    o0 = migen.Signal.like(migen_pads)
                    o1 = migen.Signal.like(migen_pads)
                    o_clk = migen.Signal()
                    for idx in range(migen_pads.nbits):
                        glue.specials += io.DDROutput(i1 = o0[idx], i2 = o1[idx], o = migen_pads[idx], clk = o_clk)
                    self.o0 = glue.from_migen(o0, name = f'{name}_o0', invert = invert)
                    self.o1 = glue.from_migen(o1, name = f'{name}_o1', invert = invert)
                    signature_members['o0'] = wiring.In(self.o0.shape())
                    signature_members['o1'] = wiring.In(self.o1.shape())
                    self.o_clk = glue.from_migen(o_clk, name = f'{name}_o_clk')
                    signature_members['o_clk'] = wiring.In(self.o_clk.shape())
                else:
                    raise RuntimeError(f'{xdr=} and {dir=} not supported yet')

            else:
                raise RuntimeError(f'{xdr=} not supported yet')

        self.signature = wiring.Signature(signature_members)
        assert self.signature.is_compliant(self)

    def __str__(self):
        return f'<PadsProxy: {self.signature}>'

class PlatformProxy:
    def __init__(self, glue):
        self.glue = glue

    def request(self, name, number = None, *, dir = None, xdr = None):
        migen_pads = self.glue.platform.request(name, number)

        if number is not None:
            name = f'{name}_{number}'

        return PadsProxy(self.glue, f'pad_{name}', migen_pads, dir, xdr)

    @property
    def device(self):
        return self.glue.platform.device
