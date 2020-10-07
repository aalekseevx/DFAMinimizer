from collections import deque
from itertools import product
from types import SimpleNamespace
from typing import Dict, List

# Everything is actually a namespace,
# Named for convenience and type checks
Automation = SimpleNamespace
State = SimpleNamespace
Transmission = SimpleNamespace

DEATH_STATE = State(
    name="bad_words_die_here",
    is_terminal=False
)

COMPONENT_NOT_SET = -1


def add_fake_vertex(dfa: Automation) -> None:
    dfa.states.append(DEATH_STATE)

    for state in dfa.states:
        for letter in dfa.alphabet:
            found = False
            for possible_dest in dfa.states:
                found |= Transmission(
                    source=state.name,
                    dest=possible_dest.name,
                    by=letter
                ) in dfa.transmissions
            if not found:
                dfa.transmissions.append(Transmission(
                    source=state.name,
                    dest=DEATH_STATE.name,
                    by=letter
                ))


def get_reversed_adjacency_list(dfa: Automation) -> Dict:
    result = dict((state.name, []) for state in dfa.states)
    for transmission in dfa.transmissions:
        result[transmission.dest].append(transmission)
    return result


def dfs(dfa: Automation, state: str, reachable: List[str]) -> None:
    if state in reachable:
        return
    reachable.append(state)
    for edge in dfa.transmissions:
        if edge.source == state:
            dfs(dfa, edge.dest, reachable)


def get_reachable_from_start(dfa: Automation) -> List[str]:
    reachable = []
    dfs(dfa, dfa.start, reachable)
    return reachable


def build_table(dfa: Automation) -> Dict:
    rev = get_reversed_adjacency_list(dfa)
    queue = deque()
    nonequivalent = dict(((v1.name, v2.name), False) for v1, v2 in product(dfa.states, dfa.states))

    for v1 in dfa.states:
        for v2 in dfa.states:
            if not nonequivalent[v1.name, v2.name] and v1.is_terminal != v2.is_terminal:
                nonequivalent[v1.name, v2.name] = True
                nonequivalent[v2.name, v1.name] = True
                queue.append((v1.name, v2.name))

    while len(queue) > 0:
        v1, v2 = queue.popleft()
        for letter in dfa.alphabet:
            for before_v1, before_v2 in product(rev[v1], rev[v2]):
                if before_v1.by != letter or before_v2.by != letter:
                    continue
                if not nonequivalent[before_v1.source, before_v2.source]:
                    nonequivalent[before_v1.source, before_v2.source] = True
                    nonequivalent[before_v2.source, before_v1.source] = True
                    queue.append((before_v1.source, before_v2.source))
    return nonequivalent


def minimize(dfa: Automation) -> Automation:
    add_fake_vertex(dfa)
    reachable = get_reachable_from_start(dfa)
    nonequivalent = build_table(dfa)

    component = dict((state.name, COMPONENT_NOT_SET) for state in dfa.states)

    next_component = 0
    will_be_terminal = []
    if DEATH_STATE.name in reachable:
        for state in dfa.states:
            if not nonequivalent[DEATH_STATE.name, state.name]:
                component[state.name] = next_component
        will_be_terminal.append(False)
        next_component += 1

    for state in dfa.states:
        name = state.name
        if name not in reachable:
            continue
        if component[name] == COMPONENT_NOT_SET:
            will_be_terminal.append(False)
            component[name] = next_component
            for next_ in dfa.states:
                if not nonequivalent[name, next_.name]:
                    will_be_terminal[COMPONENT_NOT_SET] |= next_.is_terminal
                    component[next_.name] = next_component
            next_component += 1

    new_dfa = Automation()
    new_dfa.states = [State(
        name=str(id_),
        is_terminal=will_be_terminal[id_]
    ) for id_ in range(next_component)]
    new_dfa.start = str(component[dfa.start])
    new_dfa.alphabet = dfa.alphabet

    new_dfa.transmissions = []
    for edge in dfa.transmissions:
        c1 = component[edge.source]
        c2 = component[edge.dest]
        if c1 != COMPONENT_NOT_SET and c2 != COMPONENT_NOT_SET:
            new_dfa.transmissions.append(Transmission(
                source=str(component[edge.source]),
                dest=str(component[edge.dest]),
                by=edge.by
            ))

    return new_dfa


def determinate(fa: Automation) -> Automation:
    queue = deque()
    queue.append(frozenset({fa.start}))
    in_queue = set()
    in_queue.add(frozenset({fa.start}))

    new_dfa = Automation()
    new_dfa.start = fa.start
    new_dfa.alphabet = fa.alphabet
    new_dfa.states = []
    new_dfa.transmissions = []

    while len(queue) > 0:
        state = queue.popleft()
        is_terminal = any([State(name=i, is_terminal=True) in fa.states for i in state])
        cur_name = "#".join(sorted(state))
        new_dfa.states.append(State(
            name=cur_name,
            is_terminal=is_terminal
        ))
        for letter in fa.alphabet:
            new_set = set()
            for edge in fa.transmissions:
                if edge.source in state and edge.by == letter:
                    new_set.add(edge.dest)
            next_name = "#".join(sorted(new_set))
            new_dfa.transmissions.append(Transmission(
                source=cur_name,
                dest=next_name,
                by=letter
            ))
            if frozenset(new_set) not in in_queue:
                queue.append(frozenset(new_set))
                in_queue.add(frozenset(new_set))
    return new_dfa
