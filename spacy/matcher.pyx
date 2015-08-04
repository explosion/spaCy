class MatchState(object):
    def __init__(self, token_spec, ext):
        self.token_spec = token_spec
        self.ext = ext
        self.is_final = False

    def match(self, token):
        for attr, value in self.token_spec:
            if getattr(token, attr) != value:
                return False
        else:
            return True

    def __repr__(self):
        return '<spec %s>' % (self.token_spec)


class EndState(object):
    def __init__(self, entity_type, length):
        self.entity_type = entity_type
        self.length = length
        self.is_final = True

    def __call__(self, token):
        return (self.entity_type, ((token.i+1) - self.length), token.i+1)

    def __repr__(self):
        return '<end %s>' % (self.entity_type)


class Matcher(object):
    def __init__(self, patterns):
        self.start_states = []
        for token_specs, entity_type in patterns:
            state = EndState(entity_type, len(token_specs))
            for spec in reversed(token_specs):
                state = MatchState(spec, state)
            self.start_states.append(state)

    def __call__(self, tokens):
        queue = list(self.start_states)
        matches = []
        for token in tokens:
            next_queue = list(self.start_states)
            for pattern in queue:
                if pattern.match(token):
                    if pattern.ext.is_final:
                        matches.append(pattern.ext(token))
                    else:
                        next_queue.append(pattern.ext)
            queue = next_queue
        return matches
