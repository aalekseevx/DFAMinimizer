from collections import deque
from itertools import product


def add_faked_vertex(dfa):
    states = dfa['states']
    dfa['states'].append({
        "name": "bad_words_die_here",
        "is_terminal": False
    })

    for state in states:
        for letter in dfa['alphabet']:
            found = False
            for possible_to in states:
                found |= {'from': state['name'], 'to': possible_to['name'], 'by': letter} in dfa['transmissions']
            if not found:
                print("added smth to dfa", state['name'], letter)
                dfa['transmissions'].append({
                    'from': state['name'],
                    'to': 'bad_words_die_here',
                    'by': letter
                })


def get_reversed_edges(dfa):
    result = dict((state['name'], []) for state in dfa['states'])
    for edge in dfa['transmissions']:
        result[edge['to']].append(edge)
    return result


def dfs(dfa, state, reachable):
    if state in reachable:
        return
    reachable.append(state)
    for edge in dfa['transmissions']:
        if edge['from'] == state:
            dfs(dfa, edge['to'], reachable)


def get_reachable(dfa):
    reachable = []
    dfs(dfa, dfa['start'], reachable)
    return reachable


def build_table(dfa):
    rev = get_reversed_edges(dfa)
    deq = deque()
    states = dfa['states']
    marked = dict(((v1['name'], v2['name']), False) for v1, v2 in product(states, states))

    for v1 in states:
        for v2 in states:
            if not marked[v1['name'], v2['name']] and v1['is_terminal'] != v2['is_terminal']:
                marked[v1['name'], v2['name']] = True
                marked[v2['name'], v1['name']] = True
                deq.append((v1['name'], v2['name']))

    while len(deq) > 0:
        v1, v2 = deq.popleft()
        for letter in dfa['alphabet']:
            for r in rev[v1]:
                for s in rev[v2]:
                    if r['by'] != letter or s['by'] != letter:
                        continue
                    rn = r['from']
                    sn = s['from']
                    if not marked[rn, sn]:
                        marked[rn, sn] = marked[sn, rn] = True
                        deq.append((rn, sn))
    return marked


def minimize(dfa):
    add_faked_vertex(dfa)
    reachable = get_reachable(dfa)
    marked = build_table(dfa)

    component = dict((state['name'], -1) for state in dfa['states'])

    print(reachable)
    print(marked)

    next_component = 0
    will_be_terminal = []
    if "bad_words_die_here" in reachable:
        for state in dfa['states']:
            if not marked["bad_words_die_here", state['name']]:
                component[state['name']] = next_component
        will_be_terminal.append(False)
        next_component += 1

    for state in dfa['states']:
        name = state['name']
        if name not in reachable:
            continue
        if component[name] == -1:
            will_be_terminal.append(False)
            component[name] = next_component
            print("component", next_component)
            for nexta in dfa['states']:
                if not marked[name, nexta['name']]:
                    print(nexta['name'])
                    will_be_terminal[-1] |= nexta['is_terminal']
                    component[nexta['name']] = next_component
            next_component += 1

    new_dfa = dict()

    new_dfa['states'] = [{
        'name': str(idx),
        'is_terminal': will_be_terminal[idx]
    } for idx in range(next_component)]

    new_dfa['start'] = str(component[dfa['start']])
    new_dfa['alphabet'] = dfa['alphabet']

    new_dfa['transmissions'] = []
    for edge in dfa['transmissions']:
        c1 = component[edge['from']]
        c2 = component[edge['to']]
        if c1 != -1 and c2 != -1:
            new_dfa['transmissions'].append({
                'from': str(component[edge['from']]),
                'to': str(component[edge['to']]),
                'by': edge['by']
            })
    # new_dfa['transmissions'] = list(set(new_dfa['transmissions']))

    return new_dfa


def determinater(dfa):
    que = deque()
    que.append(frozenset({dfa['start']}))

    new_dfa = dict()

    new_dfa['start'] = dfa['start']
    new_dfa['alphabet'] = dfa['alphabet']
    new_dfa['states'] = []
    new_dfa['transmissions'] = []

    used = set()
    used.add(frozenset({dfa['start']}))

    while len(que) > 0:
        q = que.popleft()
        is_terminal = any([{'name': i, 'is_terminal': True} in dfa['states'] for i in q])
        cur_name = "#".join(sorted(q))
        new_dfa['states'].append({
            'name': cur_name,
            'is_terminal': is_terminal
        })
        for letter in dfa['alphabet']:
            new_set = set()
            for edge in dfa['transmissions']:
                if edge['from'] in q and edge['by'] == letter:
                    new_set.add(edge['to'])
            next_name = "#".join(sorted(new_set))
            new_dfa['transmissions'].append({
                'from': cur_name,
                'to': next_name,
                'by': letter
            })
            if frozenset(new_set) not in used:
                que.append(frozenset(new_set))
                used.add(frozenset(new_set))
    return new_dfa
