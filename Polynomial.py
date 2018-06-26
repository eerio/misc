#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
This module implements an interpreter for the Polynomial esoteric language
"""
from collections import namedtuple
from typing import List, Tuple, Set

import numpy as np

Operation = namedtuple('Operation', ['operation', 'operand'])


def clear_roots(_roots: np.ndarray) -> np.ndarray:
    """Eliminate almost-zeros and complex conjugates"""
    _roots.real[abs(_roots.real) < 1e-11] = 0
    _roots.imag[abs(_roots.imag) < 1e-11] = 0
    _roots = _roots[roots.imag >= 0]  # if b in (a+bi) < 0, it's a NOP for us
    return _roots


def parse_monomial(monomial: str) -> Tuple[int, int]:
    """
    Take a single monomial-string and extract its coefficient and power of x

    Example:
    '+x^10'         ->  1,          10
    '-4827056x^9'   ->  -4827056,   9
    """
    assert monomial[0] in ['+', '-']

    if 'x' in monomial:  # case: +x^n
        ind = monomial.index('x')
        if not monomial[ind-1].isdigit():
            monomial = monomial[0] + '1' + monomial[1:]

    if 'x^' in monomial:
        coefficient_end = monomial.index('x^')
        power_beginning = coefficient_end + 2
        power = int(monomial[power_beginning:])
    elif 'x' in monomial and '^' not in monomial:
        coefficient_end = monomial.index('x')
        power = 1
    elif 'x' not in monomial and '^' not in monomial:
        coefficient_end = len(monomial)
        power = 0
    else:
        raise Exception('Number in a wrong format')

    coefficient = int(monomial[:coefficient_end])
    return coefficient, power


def parse_polynomial(polynomial: str) -> List[Tuple[int, int]]:
    """
    Take the whole Polynomial program as a string and perform parsing on its
    each element. Return a sequence of [(coefficient, power of x)];
    powers will be in descending order, but some of them can be missing;

    Example:
    f(x) = x^4 - 3x^2 + 2
    -> [(1, 4), (-3, 2), (2, 0)]
    """
    polynomial = polynomial.split()[2:]
    # first element can go without sign, if it's a +
    if polynomial[0] != '-':
        polynomial = ['+'] + polynomial

    # merge monomial with its sign
    merged = []
    for i in range(0, len(polynomial), 2):  # len(pol) always is divisible by 0
        merged += [polynomial[i] + polynomial[i+1]]
    return [parse_monomial(i) for i in merged]


def get_coefficients(_pairs: List[tuple]) -> List[int]:
    """
    Take a sequence like [(coefficient, power of x)] and add zeros where are
    they missing
    """
    _coefficients = []
    power_counter = _pairs[0][1]  # highest coefficient
    for pair in _pairs:
        # add missing coefficients
        while pair[1] != power_counter:
            _coefficients += [0]
            power_counter -= 1

        # add actual coefficients
        _coefficients += [pair[0]]
        power_counter -= 1
    return _coefficients


def generate_primes():
    _primes = {2}
    yield 2
    current = 3
    while True:
        if all(current % i != 0 for i in _primes):
            # nothing has divided our prime - it is a prime
            _primes.add(current)
            yield current
        current += 2  # omit even numbers


def is_almost_integer(x: float, tol=1e-11) -> bool:
    """
    Check if a float is almost an integer
    """
    return abs(x - int(round(x, 8))) < tol


def get_actual_zeros(_roots: np.ndarray) -> List[complex]:
    """
    Essential thing about parsing Polynomial code - take original polynomial's
    zeros and find the actual operations that they correspond to
    """
    # todo: the complexity can be decreased from primes*_roots to some log
    # todo: by checking the roots that have been already calculated
    prime_gen = generate_primes()
    primes = [next(prime_gen) for _ in _roots]

    commands = [0 for _ in _roots]
    for prime in primes:
        for root in _roots:
            if root.imag:  # a+bi -> a + (p^b)i
                exp = np.log(root.imag) / np.log(prime)
            else:  # a -> p^a
                if root.real < 0:
                    # -root.real to get abs and -np.log to save the orig. sign
                    exp = -np.log(-root.real) / np.log(prime)
                else:
                    exp = np.log(root.real) / np.log(prime)

            # if exp is int or almost-int - we found it!
            # int_exp is our actual zero - so the operation
            if is_almost_integer(exp):
                int_exp = int(round(exp, 8))
                if root.imag:
                    operand, operator = root.real, int_exp * 1j
                    # eliminate operand==0.99999987 etc.
                    if is_almost_integer(operand):
                        operand = int(round(operand, 8))
                else:
                    operand, operator = 0, int_exp
                # sorting by making this lookup in the primes' order table
                commands[primes.index(prime)] = complex(operand + operator)
    return commands


def translate_to_python(polynomial_code: List[complex]) -> str:
    translation = {
        -1j: 'print(chr(ACC))',
        -2j: 'ACC = ord(input())',
        1j: 'ACC += {}',
        2j: 'ACC -= {}',
        3j: 'ACC *= {}',
        4j: 'ACC /= {}',
        5j: 'ACC %= {}',
        6j: 'ACC **= {}',
        1: 'if ACC > 0:',
        2: '',
        3: 'if ACC < 0:',
        4: 'if not ACC:',
        5: 'while ACC > 0:',
        6: '',
        7: 'while ACC < 0:',
        8: 'while not ACC:'
    }

    python_code = 'ACC = 0\n'

    indent = 0
    for cmd in pol_code:
        if cmd == (0 + 1j):
            cmd = -1j
        elif cmd == (0 + 2j):
            cmd = -2j

        python_code += '\t' * indent
        if cmd.imag:
            python_code += translation[int(cmd.imag) * 1j].format(int(cmd.real))
        else:
            python_code += translation[int(cmd.real)]
        python_code += '\n'

        if cmd in {1, 3, 4, 5, 7, 8}:
            indent += 1
        elif cmd in {2, 6}:
            indent -= 1

    return python_code

# quick testing
assert is_almost_integer(0.99999999999997102)
assert not is_almost_integer(0.99)

prog = 'f(x) = x^10 - 4827056x^9 + 1192223600x^8 - 8577438158x^7 + 958436165464x^6 - 4037071023854x^5 + 141614997956730x^4 - 365830453724082x^3 + 5225367261446055x^2 - 9213984708801250x + 21911510628393750'
# Hello, World! doesn't compile
# prog = 'f(x) = x^54 - 159014x^53 + 10832073396865804x^52 - 1722454995853645185024x^51 + 37968621468067227708480815104x^50 - 6048436172078846536054214083215360x^49 - 233513143301713321053926514246008438784x^48 + 1104146527973661777408036024159387365933056x^47 - 43427940760660892945598234855622393627754364928x^46 + 67688151387034834407174775878348678887678180065280x^45 - 2657323397811390386816113812836066598878541383083229182x^44 + 1750284245331664692109566288590033450135765470086567034878x^43 - 66462310637170791141330436813018840528707142797162918925303806x^42 + 20508128690597856095696899775729835128839331997155438812840591358x^41 - 664953230461190852547732663527306948596506725237756131883009775239166x^40 + 122666463513285791263166623998020333809641694974891527172108001766014974x^39 - 2290339732715482683303962242601771918911509803450296139283376474479399010302x^38 + 333681206682071257276765622169335904551081599525895157749622024410862633091070x^37 - 1691043431739585500544644861024318773165895772478850636648655229589277769014968318x^36 + 200506166911493278122043091578573690630915822238274576692536396738642535022472462334x^35 - 83725352136727902926962688002085013348571758969699327995437883996918505898393112412158x^34 + 8946701875864986004178866146568026543826377674206253421423964436944549188572512744636414x^33 - 1867315954108076983102178980404722124954606614812493711046674205982894462255753012843642878x^32 + 178324449027542424363250070678452160645175392388973092115587091266832446376253808451931602942x^31 - 24291196173290792733633389253959325279211027629620980716292664144523119832413508515604964835326x^30 + 2051361313277806101971735175010721323823623545474630082713676031861264604659894615015106038202366x^29 - 204163318930245521138048084566822704550940204786829904381641555821279624471050262962488593524719614x^28 + 15080204889675869155229234744312762198619136509808788153390711130175410235109921892971369525296496638x^27 - 1165291326138700992648690286268194728713765396851822888922293042494539382622438040850689893573528125438x^26 + 74455666269114358239917407447450883116392692238031999396368360323797637882097034155445411572501551513598x^25 - 4629813507931028276481888188824918837219940394558223324294713679828523226590836146159419165677988974952446x^24 + 253120956733554432342716622232076867923990466385729228242480842746036367109236814280617493808254752667992062x^23 - 12935074231319533186983493987243575840365401040882648745356769581430267310941451311894303395892917187039461374x^22 + 598913063059871613059857216856855349855419761967359474402923993393922286606408014770709182577971747789238960126x^21 - 25428508737739962276270688610109187572552304592436884974847563375647270022873810881862347086815806954727658225662x^20 + 988075525812553477917947118187566933771383003967243891018665745909746387720410669543775339912470070203350513614846x^19 - 34974169531686082193562459271768002009744513364736394486295709944600099597472906094246515756034869419547478867312638x^18 + 1131815654865400099721068380879494797357578573000978123266770256219841969966466292315303189575522430114658452248723454x^17 - 33333243367066790224431125737877702592396473433676485170092104273794119865956405762749777296265621241096608710368690174x^16 + 892264657182917347092519064707331396991280027881775637162618455630037117552251223731760472327631168507410442258403557374x^15 - 21741234185793763082357467767610152549960037645439852577400502876137832861902450604589029830428630800969050504520911552510x^14 + 477743401378059186285442060198126775727720768799991712595952810072435362385423036993075850469213290973558290972495134588926x^13 - 9542386958914044777985633223358827925072853726403754987291921876055021910330691028409034466645850263821631147144589476888574x^12 + 170373657119042581679392061752246883211700633236029252140524140404116909796029987541347425321627477671207061587436661802795006x^11 - 2749764955487032211189043031405167033392562632980461084259430732124101539469658631267867961079629561250003844967312558638759934x^10 + 39258870077914541482854786591008101985140318175933710685982149707499006040540918873742652203012485463461181385232920427641176062x^9 - 500368492335132183249328269334693420237229115021360007044007047308659390943642645302624438601527360932151837223729879018719150078x^8 + 5561474165691513638632263097940791619157749550438413179410744745968666079707113111702893276550591486283330334999248957967519711230x^7 - 53880783522289363454704538003114570363811073301017229192681339922824957590137011676197017433885609211428303922108095981658814021630x^6 + 445288801638974965851448060362741780190759776482802809915713807735430669749072211419415506701161594212827516720492113889326434091006x^5 - 3062244326655950294268213743871987045997296637980493381720979841832789151604468970705217772640392632442086114584286495283795927760894x^4 + 17350497861833021048265568696066512194485118861967772235263366259072517869159731356876777820098774378356979847504601682094845149052926x^3 - 74168531044100993077468285584515190766733489300066134507874699191841424986708021389184383419592112291881531106870872614137017669779454x^2 + 228571929129635500353661243768318776163922747079196359396738280844215833818180963007061674605170476519898831960207022976332263187283966x - 611392605770821583281602313540767104622218840531412047272348323116466189132132314542079626967192155939298340170675960484343482356334590'

# todo: parser could use yielding and save some memory
pairs = parse_polynomial(prog)
coefficients = get_coefficients(pairs)
roots = np.roots(coefficients)
roots = clear_roots(roots)
pol_code = get_actual_zeros(roots)
python_code = translate_to_python(pol_code)

exec(python_code)
