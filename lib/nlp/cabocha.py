from collections import namedtuple
import CaboCha


Token = namedtuple('Token', 'surface normalized_surface feature ne')


def token2namedtuple(token):
    return Token(token.surface, token.normalized_surface, token.feature, token.ne)


def parse(sentence):
    p = CaboCha.Parser('-n 2')
    tree = p.parse(sentence)

    chunks = [dict() for i in range(tree.chunk_size())]
    for i in range(tree.chunk_size()):
        chunk = tree.chunk(i)

        dest = chunk.link
        if dest >= 0:
            chunks[dest]["linked_by"] = chunks[dest].get("linked_by", []) + [i]

        tokens = [token2namedtuple(tree.token(chunk.token_pos + j)) for j in range(chunk.token_size)]
        chunks[i]["tokens"] = tokens
        chunks[i]["func"] = tokens[chunk.func_pos]
        chunks[i]["head"] = tokens[chunk.head_pos]
        for attr in ('link', 'score'):
            chunks[i][attr] = getattr(chunk, attr)
    return chunks
