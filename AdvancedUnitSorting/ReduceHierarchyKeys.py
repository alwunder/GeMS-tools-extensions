from os.path import commonprefix

def reduce_hierarchy_keys(keys):
    # Sort keys to ensure proper prefix matching
    keys = sorted(keys)

    # Step 1: Remove keys that are prefixes of other keys
    reduced = []
    for i, key in enumerate(keys):
        is_prefix = False
        for other_key in keys[i + 1:]:
            if other_key.startswith(key + "-"):
                is_prefix = True
                break
        if not is_prefix:
            reduced.append(key)

    # Step 2: Find common prefix among reduced keys
    def split_parts(k): return k.split("-")
    split_keys = list(map(split_parts, reduced))

    # Transpose to find shared prefix components
    common_parts = []
    for parts in zip(*split_keys):
        if all(p == parts[0] for p in parts):
            common_parts.append(parts[0])
        else:
            break

    # Step 3: Strip common prefix
    prefix_len = len(common_parts)
    final = ["-".join(parts[prefix_len:]) for parts in split_keys]

    return final, "-".join(common_parts) if common_parts else None

# Example usage
keys = [
    "hk01-01-01",
    "hk01-01-01-01",
    "hk01-01-01-02",
    "hk01-01-02",
    "hk01-01-01-01-01",
    "hk01-01-01",
    "hk01-01-01-01-01",
    "hk01-01-01",
    "hk01-01-01",
    "hk01-01-01",
    "hk01-01-01-01-01",
    "hk01-01-01",
    "hk01-01-01",
    "hk01-01-02",
    "hk01-01-02",
    "hk01-01-02",
    "hk01-01-02",
    "hk01-01-03-02-02-02",
    "hk01-01-03-02-02-03",
    "hk01-01-03-02-02-04",
    "hk01-01-03-02-02-04",
    "hk01-01-03-02-03",
    "hk01-01-03-02-03",
    "hk01-01-04"
]

reduced, common_prefix = reduce_hierarchy_keys(keys)

print("Common prefix:", common_prefix)
print("Reduced keys:")
for r in reduced:
    print("  ", r)
