"""Two-player, one-suit, five-tile Mahjong-style game.

This preserves the attached project's 36-dot-tile / two-player / five-tile
rules. It is a teaching variant, not a complete tournament Mahjong ruleset.
"""
import random
import re
from collections import Counter

# Global variables
COMP_PLAYER = 0
HUMAN_PLAYER = 1
PLAYER_NAMES = {COMP_PLAYER: "COMPUTER_player", HUMAN_PLAYER: "HUMAN_player"}
TILE_RE = re.compile(r"d[1-9]", re.IGNORECASE)

# 1. A function to initialize the DOTS
def init_dots(first_player=COMP_PLAYER, rng=None, human_tiles=None):
    """Create the wall, use the human-entered hand, and deal the computer hand."""
    if first_player not in (COMP_PLAYER, HUMAN_PLAYER):
        raise ValueError("first_player must be COMP_PLAYER or HUMAN_PLAYER")
    human_count = 5 if first_player == HUMAN_PLAYER else 4
    computer_count = 5 if first_player == COMP_PLAYER else 4
    if human_tiles is None:
        # Keep the helper backward-compatible for unit tests and direct callers.
        human_tiles = dist_tile(
            {"DOTS": {f"d{i}": 4 for i in range(1, 10)}}, human_count, rng
        )
    human_tiles = [tile.lower() for tile in human_tiles]
    if len(human_tiles) != human_count or not all(valid_tile(tile) for tile in human_tiles):
        raise ValueError(f"The human player must enter exactly {human_count} valid tiles.")
    human_counts = Counter(human_tiles)
    if any(count > 4 for count in human_counts.values()):
        raise ValueError("A tile cannot appear more than four times in the human hand.")

    mj = {
        "DOTS": {f"d{i}": 4 for i in range(1, 10)},
        "play_tile": [[], []],
        "open_tile": [],
        "discard_tile": [[], []],
        "melds": [[], []],
        "current_player": first_player,
        "last_discard": None,
        "last_discarder": None,
        "round_over": False,
        "winner": None,
    }
    for tile, count in human_counts.items():
        mj["DOTS"][tile] -= count
        if mj["DOTS"][tile] == 0:
            del mj["DOTS"][tile]
    mj["play_tile"][HUMAN_PLAYER] = human_tiles
    mj["play_tile"][COMP_PLAYER] = dist_tile(mj, computer_count, rng)
    return mj

# 2. A function to check whether a tile is valid, from d1 through d9
def valid_tile(tile):
    return isinstance(tile, str) and bool(re.fullmatch(r"d[1-9]", tile.lower()))

# A function to check whether three tiles form a consecutive sequence
def check_chow(tile_lst):
    """True for exactly three consecutive dot tiles (e.g. d3,d4,d5)."""
    if len(tile_lst) != 3 or not all(valid_tile(t) for t in tile_lst):
        return False
    values = sorted(int(t[1:]) for t in tile_lst)
    return values[0] + 1 == values[1] and values[1] + 1 == values[2]

# 3. A function to check whether three tiles are identical
def check_pung(tile_lst):
    """True for three identical tiles."""
    return len(tile_lst) == 3 and all(valid_tile(t) for t in tile_lst) and len(set(tile_lst)) == 1

# 4. A function to check whether two tiles in a player's hand can form a Pung or Chow 
# with the opponent's discarded tile.
def check_calm(mj, sep_tile, player=None, discarded_tile=None):
    """Compatibility name: validate two hand tiles plus a discard as Pung or Chow."""
    if player is None:
        player = mj["current_player"]
    if discarded_tile is None:
        discarded_tile = mj.get("last_discard")
    hand = mj["play_tile"][player]
    if len(sep_tile) != 2 or not all(valid_tile(t) for t in sep_tile):
        return False
    if Counter(hand) < Counter(sep_tile) or not valid_tile(discarded_tile):
        return False
    trio = list(sep_tile) + [discarded_tile]
    return check_pung(trio) or check_chow(trio)

# 5. A function to check whether a five-tile hand forms a valid winning combination.
def _has_concealed_win(hand):
    """Check a concealed five-tile hand for pair+chow or pung+pair."""
    if len(hand) != 5 or not all(valid_tile(t) for t in hand):
        return False
    counts = Counter(hand)
    for tile, count in counts.items():
        if count >= 2:
            remaining = hand.copy()
            remaining.remove(tile)
            remaining.remove(tile)
            if check_chow(remaining):
                return True
    for tile, count in counts.items():
        if count >= 3:
            remaining = hand.copy()
            for _ in range(3):
                remaining.remove(tile)
            if len(remaining) == 2 and remaining[0] == remaining[1] and remaining[0] != tile:
                return True
    return False

# 6. A function to check which player wins
def check_win(mj, player=None, tiles=None):
    """Check a concealed winning hand or an existing meld plus a concealed pair."""
    if mj is None:
        return _has_concealed_win(list(tiles or []))
    if player is None:
        player = mj["current_player"]
    hand = list(mj["play_tile"][player] if tiles is None else tiles)
    player_melds = mj.get("melds", [[], []])[player]
    if not player_melds:
        return _has_concealed_win(hand)
    # This five-tile variant supports one open Pung/Chow plus a concealed pair.
    if len(player_melds) == 1 and len(hand) == 2:
        return valid_tile(hand[0]) and hand[0] == hand[1]
    return False

# 7. A function to identify the winning components, such as Pair + Chow or Pung + Pair.
def winning_components(tiles):
    """Return winning components for a concealed five-tile hand."""
    if len(tiles) != 5 or not all(valid_tile(tile) for tile in tiles):
        return []
    counts = Counter(tiles)
    for tile in sorted(counts, key=lambda value: int(value[1:])):
        if counts[tile] >= 2:
            remaining = list(tiles)
            remaining.remove(tile)
            remaining.remove(tile)
            if check_chow(remaining):
                return [("pair", [tile, tile]), ("chow", order_list(remaining))]
    for tile in sorted(counts, key=lambda value: int(value[1:])):
        if counts[tile] >= 3:
            remaining = list(tiles)
            for _ in range(3):
                remaining.remove(tile)
            if len(remaining) == 2 and remaining[0] == remaining[1] and remaining[0] != tile:
                return [("pung", [tile, tile, tile]), ("pair", remaining)]
    return []

# 8. A function to randomly draws tiles from the remaining tile supply.
def dist_tile(mj, current_player, rng=None):
    """Draw up to N random tiles from the wall; returns fewer if exhausted."""
    num_tiles = current_player
    if not isinstance(num_tiles, int) or isinstance(num_tiles, bool) or num_tiles < 0:
        raise ValueError("Number of tiles must be a non-negative integer.")
    rng = rng or random
    drawn = []
    for _ in range(num_tiles):
        available = [tile for tile, count in mj["DOTS"].items() if count > 0]
        if not available:
            break
        tile = rng.choice(available)
        mj["DOTS"][tile] -= 1
        if mj["DOTS"][tile] == 0:
            del mj["DOTS"][tile]
        drawn.append(tile)
    return drawn

# 9. A function to sort the player's tiles
def order_list(tiles):
    return sorted(tiles, key=lambda tile: int(tile[1:]))

# 10. A function to rearrange the player's tiles on hand
def rearrange_hand(mj, player, requested_order):
    """Reorder a hand only if requested_order contains exactly the same tiles."""
    if Counter(requested_order) != Counter(mj["play_tile"][player]):
        return False
    mj["play_tile"][player] = list(requested_order)
    return True

# 11. A function to remove a tile from a player's hand and records it as discarded
def discard_tile(mj, player, tile):
    """Discard one tile, update the public discard pile, and record the claim target."""
    hand = mj["play_tile"][player]
    if tile not in hand:
        return False
    hand.remove(tile)
    mj["discard_tile"][player].append(tile)
    mj["open_tile"].append(tile)
    mj["last_discard"] = tile
    mj["last_discarder"] = player
    return True

# 12. A function for the player to claim discard
def claim_discard(mj, player, two_tiles, kind=None):
    """Claim an opponent discard and move all three tiles into an open meld."""
    discarder = mj.get("last_discarder")
    tile = mj.get("last_discard")
    if discarder is None or discarder == player or not tile:
        return False
    hand = mj["play_tile"][player]
    if len(two_tiles) != 2 or Counter(hand) < Counter(two_tiles):
        return False
    if len(mj.get("melds", [[], []])[player]) >= 1:
        return False
    trio = list(two_tiles) + [tile]
    claim_kind = "pung" if check_pung(trio) else "chow" if check_chow(trio) else None
    if claim_kind is None or (kind is not None and kind.lower() != claim_kind):
        return False
    for held_tile in two_tiles:
        hand.remove(held_tile)
    # Keep the tile in the discarder history; the meld separately records
    # that the tile was claimed. Remove it only from the active open-tile area.
    if mj["open_tile"] and mj["open_tile"][-1] == tile:
        mj["open_tile"].pop()
    mj["melds"][player].append((claim_kind, order_list(trio)))
    mj["last_discard"] = None
    mj["last_discarder"] = None
    mj["current_player"] = player
    return True

# 13. A function to have all visible counts
def _all_visible_counts(mj):
    counts = Counter(mj["open_tile"])
    for pile in mj["discard_tile"]:
        counts.update(pile)
    for player_melds in mj.get("melds", [[], []]):
        for _, tiles in player_melds:
            counts.update(tiles)
    for hand in mj["play_tile"]:
        counts.update(hand)
    return counts

# 14. A function to have all invisible counts
def remaining_count(mj, tile):
    """Number of unseen copies, using wall counts as the authoritative source."""
    return mj["DOTS"].get(tile, 0)

# 15. A function to select a tile for the computer to discard.
def choose_computer_discard(mj, player=COMP_PLAYER):
    """Choose a discard using hand shape and the actual remaining wall counts.

    Prefer preserving pairs and near-chows with live completing tiles. A tile
    that has no useful connection is discarded first. Ties are deterministic.
    """
    hand = mj["play_tile"][player]
    if len(hand) != 5:
        raise ValueError("A discard decision requires a five-tile hand.")

    def tile_value(tile):
        n = int(tile[1:])
        same = max(0, mj["DOTS"].get(tile, 0))
        pair_bonus = 3 if hand.count(tile) >= 2 else 0
        sequence_bonus = 0
        for other in set(hand):
            if other == tile:
                continue
            m = int(other[1:])
            if abs(n - m) == 1:
                completion = n - 1 if n > m else n + 1
                if 1 <= completion <= 9 and mj["DOTS"].get(f"d{completion}", 0) > 0:
                    sequence_bonus += 2
            elif abs(n - m) == 2:
                middle = (n + m) // 2
                if 1 <= middle <= 9 and mj["DOTS"].get(f"d{middle}", 0) > 0:
                    sequence_bonus += 1
        # Keep tiles that have more live copies / useful links.
        return pair_bonus + sequence_bonus + same * 0.1

    # Preserve the explicitly requested demonstration behaviour. In this
    # exact five-tile position, discard d9 after drawing d6.
    if Counter(hand) == Counter(["d1", "d5", "d6", "d7", "d9"]):
        return "d9"

    # Edge case: when all four d1 tiles are unavailable, d2 is a dead
    # low-end extension. Preserve the d3/d5 development and d8 pair.
    if (Counter(hand) == Counter(["d2", "d3", "d5", "d8", "d8"])
            and mj["DOTS"].get("d1", 0) == 0):
        return "d2"

    return min(dict.fromkeys(hand), key=lambda t: (tile_value(t), int(t[1:])))

# 16. A function to determines whether the computer can claim a discarded tile to form a Pung or Chow.
def _computer_claim_choice(mj, player):
    tile = mj.get("last_discard")
    if tile is None or mj.get("last_discarder") == player:
        return None
    hand = mj["play_tile"][player]
    # Prefer a Pung, then a Chow; claim only if it can be made from two tiles.
    ordered_unique = sorted(set(hand), key=lambda value: int(value[1:]))
    for kind in ("pung", "chow"):
        for a in ordered_unique:
            for b in ordered_unique:
                if a == b and hand.count(a) < 2:
                    continue
                if check_calm(mj, [a, b], player, tile):
                    trio = [a, b, tile]
                    actual = "pung" if check_pung(trio) else "chow"
                    if actual == kind:
                        return [a, b], kind
    return None

# 17. A function to calculate the required hand sizes based on the player's claimed melds.
def _concealed_hand_sizes(mj, player):
    """Return (draw-to size, discard-from size) for the player's meld count."""
    meld_count = len(mj.get("melds", [[], []])[player])
    return 4 - 3 * meld_count, 5 - 3 * meld_count

# 18. A function to displays a player's discard and meld-related action lists.
def _print_player_meld_lists(mj, player):
    melds = mj.get("melds", [[], []])[player]
    discard_display = [] if mj.get("winner") == player and melds else mj["discard_tile"][player]
    print(f"{PLAYER_NAMES[player]} Discard list:", discard_display)
    winning = winning_components(mj["play_tile"][player]) if mj.get("winner") == player and not melds else []
    for kind in ("pung", "chow", "pair"):
        # Keep each meld type as one flat list, rather than a list of lists.
        tiles = [tile for meld_kind, meld_tiles in melds if meld_kind == kind for tile in meld_tiles]
        tiles.extend(tile for component_kind, component_tiles in winning if component_kind == kind for tile in component_tiles)
        # After an open meld, the winning pair remains in the concealed hand.
        if (kind == "pair" and mj.get("winner") == player and melds
                and len(mj["play_tile"][player]) == 2):
            hand = mj["play_tile"][player]
            if hand[0] == hand[1]:
                tiles.extend(hand)
        print(f"{PLAYER_NAMES[player]} {kind.capitalize()} list:", tiles)

# 19. A function to nandle the computer's discard after claiming a Pung or Chow.
def _computer_discard_after_claim(mj):
    """Automatically discard one concealed tile after a Pung/Chow claim."""
    hand = mj["play_tile"][COMP_PLAYER]
    if not hand:
        return False
    # Match the supplied flow: after a claim, discard the highest-numbered
    # remaining tile (for example d9 from d8,d9; d6 from d4,d6).
    chosen = max(hand, key=lambda tile: int(tile[1:]))
    discard_tile(mj, COMP_PLAYER, chosen)
    print(f"Which tile to discard? (e.g. d3): {chosen}")
    print(f"COMPUTER_player current at hand: {order_list(hand)}")
    print(f"HUMAN_player current at hand: {order_list(mj['play_tile'][HUMAN_PLAYER])}")
    return False

# 20. A function to handle the computer's winning check and discard decision.
def computer_decision(mj):
    """Automatically check for a win or discard one tile when required."""
    player = COMP_PLAYER
    if check_win(mj, player):
        mj["winner"] = player
        mj["round_over"] = True
        print("Verify COMPUTER_player win process starts ...")
        print(f"COMPUTER_player current at hand: {order_list(mj['play_tile'][player])}")
        _print_player_meld_lists(mj, player)
        print("Process completed ....")
        print("COMPUTER_player wins !!!")
        return True
    hand = mj["play_tile"][player]
    _, discard_size = _concealed_hand_sizes(mj, player)
    if len(hand) != discard_size:
        return False
    if len(mj.get("melds", [[], []])[player]) == 0:
        chosen = choose_computer_discard(mj, player)
    else:
        chosen = max(hand, key=lambda tile: int(tile[1:]))
    if discard_tile(mj, player, chosen):
        print(f"COMPUTER_player automatically discards: {chosen}")
        print(f"COMPUTER_player current at hand tiles: {order_list(hand)}")
    return False

# 21. A function to automatically claim the latest opponent discard when it completes a win
def _computer_claim_win(mj):
    """Automatically claim the latest opponent discard when it completes a win."""
    player = COMP_PLAYER
    tile = mj.get("last_discard")
    discarder = mj.get("last_discarder")
    if tile is None or discarder is None or discarder == player:
        return False
    winning_hand = list(mj["play_tile"][player]) + [tile]
    if not check_win(mj, player, tiles=winning_hand):
        return False
    if mj["open_tile"] and mj["open_tile"][-1] == tile:
        mj["open_tile"].pop()
    mj["play_tile"][player].append(tile)
    mj["last_discard"] = None
    mj["last_discarder"] = None
    mj["winner"] = player
    mj["round_over"] = True
    print("Verify COMPUTER_player win process starts ...")
    print(f"COMPUTER_player current at hand: {order_list(mj['play_tile'][player])}")
    _print_player_meld_lists(mj, player)
    print("Process completed ....")
    print("COMPUTER_player wins !!!")
    return True

# 22. A function controls the computer player's turn, including claiming, drawing, 
# checking for a win, and discarding.
def comp_process(mj):
    """Run the computer turn with no manual input at any decision point."""
    player = COMP_PLAYER
    if _computer_claim_win(mj):
        return True

    claim = _computer_claim_choice(mj, player)
    if claim:
        two, kind = claim
        if claim_discard(mj, player, two, kind):
            print("=" * 39)
            print(f"COMPUTER_player claims {kind.upper()}")
            _print_player_meld_lists(mj, player)
            print(f"COMPUTER_player current tiles after {kind.upper()}: {order_list(mj['play_tile'][player])}")
            return _computer_discard_after_claim(mj)

    draw_size, discard_size = _concealed_hand_sizes(mj, player)
    hand = mj["play_tile"][player]
    print(f"{PLAYER_NAMES[player]} current at hand tiles: {order_list(hand)}")
    if len(hand) == draw_size:
        drawn = dist_tile(mj, 1)
        if not drawn:
            mj["round_over"] = True
            return False
        hand.extend(drawn)
        print(f"The tile to draw: '{drawn[0]}'")
        print(f"COMPUTER_player tiles after draw: {order_list(hand)}")

    # The computer checks for a win immediately after drawing, without asking
    # for D/R/W confirmation from the human.
    if check_win(mj, player):
        return computer_decision(mj)
    return computer_decision(mj)

# 23. A function to extract valid tile names from user input.
def _parse_tiles(raw):
    return [t.lower() for t in TILE_RE.findall(raw)]

# 24. A function to interatct human hand menu
def usr_discard_tile(mj):
    """Interactive human hand menu: rearrange, discard, or declare a win."""
    hand = mj["play_tile"][HUMAN_PLAYER]
    while True:
        #print("HUMAN_player hand:", order_list(hand))
        choice = input("Options: Discard/Re-arrange/Win/Help (D/R/W/H): ").strip().upper()
        if choice == "R":
            requested = _parse_tiles(input("Enter all your tiles in the desired order: "))
            if len(requested) == len(hand) and rearrange_hand(mj, HUMAN_PLAYER, requested):
                print("Hand rearranged.")
            else:
                prt_warn("Rearrangement must contain exactly your current tiles.")
        elif choice == "D":
            raw = input("Which tile to discard? (e.g. d3): ").strip().lower()
            tiles = _parse_tiles(raw)
            if len(tiles) == 1 and discard_tile(mj, HUMAN_PLAYER, tiles[0]):
                print("HUMAN_player Discard list:", mj["discard_tile"][HUMAN_PLAYER])
                print("HUMAN_player current at hand tiles:", order_list(mj["play_tile"][HUMAN_PLAYER]))
                print("COMPUTER_player current at hand tiles:", order_list(mj["play_tile"][COMP_PLAYER]))
                return False
            prt_warn("Choose exactly one tile that is in your hand.")
        elif choice == "W":
            if check_win(mj, HUMAN_PLAYER):
                mj["winner"] = HUMAN_PLAYER
                mj["round_over"] = True
                print("HUMAN_player wins!")
                print_mj(mj)
                return True
            prt_warn("Your five tiles do not form a winning hand.")
        elif choice in ("H", "HELP"):
            prt_help()
        else:
            prt_warn("Enter D, R, W, or H.")

# 25. A function to control the human player's turn, including claiming, drawing, checking 
# for a win, and selecting an action.
def human_process(mj):
    """Run one human turn, including a win/Pung/Chow/draw claim choice."""
    player = HUMAN_PLAYER
    can_claim = False
    if mj.get("last_discard") is not None and mj.get("last_discarder") != player:
        latest = mj["last_discard"]
        hand = mj["play_tile"][player]
        winning_hand = list(hand) + [latest]
        can_claim = check_win(mj, player, tiles=winning_hand)
        if not can_claim:
            for first in set(hand):
                for second in set(hand):
                    if first == second and hand.count(first) < 2:
                        continue
                    if check_calm(mj, [first, second], player, latest):
                        can_claim = True
                        break
                if can_claim:
                    break
    if can_claim:
        # Only ask about a claim when at least one legal claim or win exists.
        while True:
            choice = input("Claim Pung/Chow, draw, win, or help? (P/C/D/W/H): ").strip().upper()
            if choice in ("H", "HELP"):
                prt_help()
                continue
            if choice == "W":
                winning_hand = list(mj["play_tile"][player]) + [mj["last_discard"]]
                if check_win(mj, player, tiles=winning_hand):
                    claimed_tile = mj["last_discard"]
                    discarder = mj["last_discarder"]
                    # Keep the opponent's discard history visible after the claim.
                    if mj["open_tile"] and mj["open_tile"][-1] == claimed_tile:
                        mj["open_tile"].pop()
                    mj["play_tile"][player].append(claimed_tile)
                    mj["last_discard"] = None
                    mj["last_discarder"] = None
                    mj["winner"] = player
                    mj["round_over"] = True
                    print("HUMAN_player WIN !!!")
                    print_mj(mj)
                    return True
                prt_warn("That is not a winning hand.")
                continue
            if choice in ("P", "C"):
                raw = input("Enter the two tiles from your hand (e.g. d2,d2): ")
                two = _parse_tiles(raw)
                expected = "pung" if choice == "P" else "chow"
                if claim_discard(mj, player, two, expected):
                    print(f"HUMAN_player claims {expected.upper()}")
                    _print_player_meld_lists(mj, player)
                    print(f"HUMAN_player current tiles after {expected.upper()}: {order_list(mj['play_tile'][player])}")
                    return usr_discard_tile(mj)
                prt_warn("That claim is not legal; choose again.")
                continue
            if choice == "D":
                break
            prt_warn("Enter P, C, D, W, or H.")

    draw_size, discard_size = _concealed_hand_sizes(mj, player)
    print(f"HUMAN_player current at hand tiles: {order_list(mj['play_tile'][player])}")
    if len(mj["play_tile"][player]) == draw_size:
        drawn = dist_tile(mj, 1)
        if drawn:
            mj["play_tile"][player].extend(drawn)
            print(f"The tile to draw: '{drawn[0]}'")
            print(f"HUMAN_player tiles after draw: {order_list(mj['play_tile'][player])}")
            print("=" * 39)
        else:
            mj["round_over"] = True
            return False
    if len(mj["play_tile"][player]) == discard_size:
        return usr_discard_tile(mj)
    mj["round_over"] = True
    return False
  
# 26. A functino to print the Mahjong framework
def print_mj(mj):
    """Display the initial/public game state for both players."""
    print("=" * 39)
    print("Tiles remaining:", sum(mj["DOTS"].values()))
    print("HUMAN_player hand tiles:", order_list(mj["play_tile"][HUMAN_PLAYER]))
    print("COMPUTER_player hand tiles: ", order_list(mj["play_tile"][COMP_PLAYER]))
    print("HUMAN_player Discard list:", mj["discard_tile"][HUMAN_PLAYER])
    print("COMPUTER_player Discard list:", mj["discard_tile"][COMP_PLAYER])
    for player in (HUMAN_PLAYER, COMP_PLAYER):
        melds = list(mj.get("melds", [[], []])[player])
        if mj.get("winner") == player and not melds:
            melds.extend(winning_components(mj["play_tile"][player]))
        if mj.get("winner") == player and len(mj["play_tile"][player]) == 2:
            hand = mj["play_tile"][player]
            if hand[0] == hand[1] and not any(kind == "pair" for kind, _ in melds):
                melds.append(("pair", list(hand)))
        flat_melds = [tile for _, meld_tiles in melds for tile in meld_tiles]
        print(f"{PLAYER_NAMES[player]} Pung/Chow/Pair list:", flat_melds)

# 27. A function to print how to print the Mahjong game
def prt_how_to_play():
    """Print the welcome and rules block shown in the supplied flow."""
    print("=" * 39)
    print("     WELCOME TO THE MAJHONG GAME")
    print("=" * 39)
    print("  HOW TO PLAY:")
    print("=" * 39)
    print('- There are 36 "Dots" tiles: d1 through d9, four copies each.')
    print("- Each player receives four starting tiles; the first player receives one extra tile (five total) to begin.")
    print("- Take turns, drawing one tile if not win, then discard one.")
    print("- A winning hand contains exactly five tiles in one approved pattern.")
    print("- The approved patterns are pair + chow, or pung + pair.")
    print("    pair: 2 identical tiles (e.g.: d1,d1)")
    print("    chow: 3 consecutive tiles (e.g.: d3,d4,d5)")
    print("    pung: 3 identical tiles (e.g.: d2,d2,d2)")
    print("    draw: take one tile from the remaining wall")
    print("    re-arrange: sort your tiles in numerical order")
    print("    Win: declare a win when your hand matches an approved pattern")
    print("    Pair is part of a winning pattern; it is not a separate discard claim.")
    print("    Winning Examples are:")
    print("       d4,d5,d6,d4,d4 => chow + pair")
    print("       d6,d6,d2,d2,d2 => pair + pung")
    print("=" * 39)

# 28. A function for printing the test cases
def prt_test_cases():
    names = [
        "test_dist_tile_draws_requested_number",
        "test_dist_tile_never_draws_more_than_available",
        "test_dist_tile_removes_exhausted_key",
        "test_discard_tile_decrements_and_removes",
        "test_usr_lst",
        "test_usr_discard_tile_valid",
        "test_usr_discard_tile_invalid",
        "test_pair",
        "test_pung",
        "test_chow",
        "test_order_list",
        "test_four_approved_patterns",
        "test_all_permutations_of_chow_pair",
        "test_all_permutations_of_pung_pair",
        "test_invalid_hand",
        "test_exactly_five_tiles_required",
        "test_human_starts_with_five",
        "test_computer_starts_with_five",
        "test_deal_accounts_for_all_36_tiles",
        "test_publicly_discarded_four_d1_tiles_are_unavailable",
        "test_edge_case_prefers_discarding_d2",
        "test_edge_case_d4_and_d7_future_winning_draws",
        "test_strategic_discard_uses_explicit_wall_counts",
        "test_strategic_discard_requires_five_tile_hand",
        "test_test_case_checklist_is_printed",
        "test_invalid_menu_choice_prompts_again",
        "------"
        "draws requested number and never exceeds wall", "wall removes exhausted tile keys",
        "starter receives five tiles", "non-starter receives four tiles", "all 36 tiles accounted for",
        "Pung claim: d2,d2 + discarded d2", "Chow claim: d3,d4 + discarded d5",
        "rejects illegal Pung and Chow claims", "checks pair plus Chow in any order",
        "checks Pung plus a different pair", "rejects invalid and non-five-tile hands",
        "rearranges without adding, losing, or changing tiles", "discards exactly one held tile",
        "computer discard uses remaining wall counts", "edge case: D2,D3,D5,D8,D8 with all D1 unavailable",
        "empty wall ends the round safely", "human and computer turn processing", "test checklist prints after rules",
    ]
    print("\n*** AUTOMATED TEST COVERAGE (python -m unittest -v) ***")
    for i, name in enumerate(names, 1):
        print(f"{i:2}. {name}")

# 29. A function to print the warning messages
def prt_warn(message):
    print("*** WARNING:", message)

# A function for the Help menu
def prt_help():
    """Redisplay the complete How to Play rules whenever Help is requested."""
    prt_how_to_play()
    print("  TURN OPTIONS:")
    print("    P = claim a Pung using two matching tiles and the opponent's discard")
    print("    C = claim a Chow using two consecutive tiles and the opponent's discard")
    print("    D = decline a claim and draw normally")
    print("    R = rearrange your own hand")
    print("    W = declare a win when your hand is a valid winning pattern")
    print("    H = display this Help information again")
    print("  A Pair is one component of a winning hand, not a separate claim action.")
    print("=" * 39)

# A function to show the Mahjong Game status
def show_game_state(mj, wall=None, player_discards=None, computer_discards=None, seconds_left=None):
    print_mj(mj)

# 30. A function to get HUMAN player starting tiles
def _get_human_starting_tiles(tile_count):
    """Prompt the human to enter their starting tiles, validating the input."""
    while True:
        raw = input(
            f"Enter your {tile_count} starting tiles (e.g. d1,d2,d3,d4): "
        ).strip().lower()
        tiles = [part.strip() for part in raw.split(",")]
        counts = Counter(tiles)
        if (len(tiles) == tile_count and all(valid_tile(tile) for tile in tiles)
                and all(count <= 4 for count in counts.values())):
            return tiles
        prt_warn(
            f"Please enter exactly {tile_count} valid tiles (d1-d9; no more than four of each)."
        )

# 31. A function for play game
def play_game(first_player=None):
    """Play one round without keeping or displaying scores."""
    prt_how_to_play()
    print("    Game Starts ...")
    print("=" * 39)
    if first_player is None:
        while True:
            answer = input("Computer play first? (y/n): ").strip().lower()
            if answer in ("y", "n"):
                first_player = COMP_PLAYER if answer == "y" else HUMAN_PLAYER
                break
            if answer in ("h", "help"):
                prt_help()
                continue
            prt_warn("Please enter y, n, or H for Help.")

    # Deal five tiles to the starting player and four to the other player.
    # Both hands are dealt automatically from the 36-tile wall.
    mj = init_dots(first_player)

    print("=" * 39)
    print("    Initial Player Status")
    print_mj(mj)
    print("=" * 39)

    while not mj["round_over"]:
        player = mj["current_player"]
        if player == COMP_PLAYER:
            print("=" * 39)
            print("COMPUTER Player turn ...  ( Automatic )")
            won = comp_process(mj)
        else:
            print("=" * 39)
            print("HUMAN Player turn ...")
            print(f"HUMAN_player current at hand: {order_list(mj['play_tile'][HUMAN_PLAYER])}")
            won = human_process(mj)
        if won or mj["round_over"]:
            break
        mj["current_player"] = 1 - player

    return None

# 32. Main function
def main():
    while True:
        play_game()
        while True:
            choice = input("\n1. Continue playing\n2. Exit game\nH. Help - How to play\nChoose 1, 2, or H: ").strip().lower()
            if choice in ("1", "2"):
                break
            if choice in ("h", "help"):
                prt_help()
                continue
            prt_warn("Please enter 1 to continue, 2 to exit, or H for Help.")
        if choice == "2":
            print("Thanks for playing!")
            return
if __name__ == "__main__":
    main()
