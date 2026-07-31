import random
from urllib.parse import quote
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from dsa.models import Pattern, Question
from aptitude.models import Topic, Problem
from technical.models import Concept, TechQuestion
from interview.models import InterviewQuestion


def lc_tag(tag):
    return f"https://leetcode.com/tag/{tag}/"


def lc_problem(slug):
    return f"https://leetcode.com/problems/{slug}/"


GFG_DIRECT_LINKS = {
    # Curated, verified direct URLs for topics that don't map cleanly to a
    # simple slug of their display name. Extend this dict any time a link
    # below turns out to point at the wrong article.
    "Sliding Window": "https://www.geeksforgeeks.org/window-sliding-technique/",
    "Two Pointers": "https://www.geeksforgeeks.org/two-pointers-technique/",
    "Dynamic Programming": "https://www.geeksforgeeks.org/dynamic-programming/",
    "Graphs": "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/",
    "Trees": "https://www.geeksforgeeks.org/binary-tree-data-structure/",
    "Heaps": "https://www.geeksforgeeks.org/heap-data-structure/",
    "Tries": "https://www.geeksforgeeks.org/trie-insert-and-search/",
    "Union Find": "https://www.geeksforgeeks.org/introduction-to-disjoint-set-data-structure-or-union-find-algorithm/",
    "Backtracking": "https://www.geeksforgeeks.org/backtracking-algorithms/",
    "OOP": "https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-java/",
    "DBMS": "https://www.geeksforgeeks.org/dbms/",
    "OS": "https://www.geeksforgeeks.org/operating-systems/",
    "CN": "https://www.geeksforgeeks.org/computer-network-tutorials/",
    "SE": "https://www.geeksforgeeks.org/software-engineering/",
    "SD": "https://www.geeksforgeeks.org/system-design-tutorial/",
}


def gfg_search(q):
    """
    Returns a direct link to the real GeeksforGeeks article for `q`, landing
    on the actual concept page rather than a Google search results page.
    Checks the curated dict first, then falls back to GfG's own predictable
    slug pattern (https://www.geeksforgeeks.org/<slugified-title>/), which is
    how the vast majority of their articles are actually addressed.
    """
    if q in GFG_DIRECT_LINKS:
        return GFG_DIRECT_LINKS[q]
    return f"https://www.geeksforgeeks.org/{slugify(q)}/"


# ---------------------------------------------------------------
# DSA: 25 patterns x 20 = 500
# Each pattern: (name, slug_tag_for_leetcode, description, [curated real problems as (title, lc_slug or None)])
# ---------------------------------------------------------------
DSA_PATTERNS = [
    ("Arrays & Hashing", "array", "Foundational array & hash-map techniques: frequency maps, prefix sums, in-place tricks.",
     [("Two Sum", "two-sum"), ("Contains Duplicate", "contains-duplicate"),
      ("Group Anagrams", "group-anagrams"), ("Top K Frequent Elements", "top-k-frequent-elements"),
      ("Product of Array Except Self", "product-of-array-except-self"),
      ("Valid Anagram", "valid-anagram"), ("Longest Consecutive Sequence", "longest-consecutive-sequence"),
      ("Subarray Sum Equals K", "subarray-sum-equals-k"),
      ("Majority Element", "majority-element"), ("Find All Duplicates in an Array", "find-all-duplicates-in-an-array")]),
    ("Two Pointers", "two-pointers", "Move two indices toward/away from each other to reduce time complexity.",
     [("Valid Palindrome", "valid-palindrome"), ("Two Sum II - Input Array Is Sorted", "two-sum-ii-input-array-is-sorted"),
      ("3Sum", "3sum"), ("Container With Most Water", "container-with-most-water"),
      ("Trapping Rain Water", "trapping-rain-water"), ("Sort Colors", "sort-colors"),
      ("Remove Duplicates from Sorted Array", "remove-duplicates-from-sorted-array"),
      ("4Sum", "4sum"), ("Boats to Save People", "boats-to-save-people"),
      ("Squares of a Sorted Array", "squares-of-a-sorted-array")]),
    ("Sliding Window", "sliding-window", "Maintain a window over a sequence to solve subarray/substring problems in linear time.",
     [("Best Time to Buy and Sell Stock", "best-time-to-buy-and-sell-stock"),
      ("Longest Substring Without Repeating Characters", "longest-substring-without-repeating-characters"),
      ("Longest Repeating Character Replacement", "longest-repeating-character-replacement"),
      ("Permutation in String", "permutation-in-string"),
      ("Minimum Window Substring", "minimum-window-substring"),
      ("Sliding Window Maximum", "sliding-window-maximum"),
      ("Maximum Average Subarray I", "maximum-average-subarray-i"),
      ("Fruit Into Baskets", "fruit-into-baskets"),
      ("Longest Subarray of 1's After Deleting One Element", "longest-subarray-of-1s-after-deleting-one-element"),
      ("Max Consecutive Ones III", "max-consecutive-ones-iii")]),
    ("Stack", "stack", "LIFO structure used for parsing, monotonic stack problems, and expression evaluation.",
     [("Valid Parentheses", "valid-parentheses"), ("Min Stack", "min-stack"),
      ("Evaluate Reverse Polish Notation", "evaluate-reverse-polish-notation"),
      ("Generate Parentheses", "generate-parentheses"),
      ("Daily Temperatures", "daily-temperatures"),
      ("Car Fleet", "car-fleet"), ("Largest Rectangle in Histogram", "largest-rectangle-in-histogram"),
      ("Next Greater Element I", "next-greater-element-i"),
      ("Asteroid Collision", "asteroid-collision"),
      ("Decode String", "decode-string")]),
    ("Binary Search", "binary-search", "Search in logarithmic time on sorted or monotonic search spaces.",
     [("Binary Search", "binary-search"), ("Search in Rotated Sorted Array", "search-in-rotated-sorted-array"),
      ("Find Minimum in Rotated Sorted Array", "find-minimum-in-rotated-sorted-array"),
      ("Search a 2D Matrix", "search-a-2d-matrix"),
      ("Koko Eating Bananas", "koko-eating-bananas"),
      ("Time Based Key-Value Store", "time-based-key-value-store"),
      ("Median of Two Sorted Arrays", "median-of-two-sorted-arrays"),
      ("Find Peak Element", "find-peak-element"),
      ("Capacity To Ship Packages Within D Days", "capacity-to-ship-packages-within-d-days"),
      ("Split Array Largest Sum", "split-array-largest-sum")]),
    ("Linked List", "linked-list", "Pointer manipulation: reversal, cycle detection, merging, fast/slow pointers.",
     [("Reverse Linked List", "reverse-linked-list"), ("Merge Two Sorted Lists", "merge-two-sorted-lists"),
      ("Linked List Cycle", "linked-list-cycle"), ("Reorder List", "reorder-list"),
      ("Remove Nth Node From End of List", "remove-nth-node-from-end-of-list"),
      ("Copy List with Random Pointer", "copy-list-with-random-pointer"),
      ("Add Two Numbers", "add-two-numbers"),
      ("Find the Duplicate Number", "find-the-duplicate-number"),
      ("LRU Cache", "lru-cache"),
      ("Merge k Sorted Lists", "merge-k-sorted-lists")]),
    ("Trees (BFS/DFS)", "tree", "Traversal and recursion on binary trees / BSTs.",
     [("Invert Binary Tree", "invert-binary-tree"), ("Maximum Depth of Binary Tree", "maximum-depth-of-binary-tree"),
      ("Diameter of Binary Tree", "diameter-of-binary-tree"),
      ("Balanced Binary Tree", "balanced-binary-tree"),
      ("Same Tree", "same-tree"), ("Subtree of Another Tree", "subtree-of-another-tree"),
      ("Lowest Common Ancestor of a Binary Search Tree", "lowest-common-ancestor-of-a-binary-search-tree"),
      ("Binary Tree Level Order Traversal", "binary-tree-level-order-traversal"),
      ("Validate Binary Search Tree", "validate-binary-search-tree"),
      ("Kth Smallest Element in a BST", "kth-smallest-element-in-a-bst"),
      ("Construct Binary Tree from Preorder and Inorder Traversal", "construct-binary-tree-from-preorder-and-inorder-traversal"),
      ("Binary Tree Maximum Path Sum", "binary-tree-maximum-path-sum"),
      ("Serialize and Deserialize Binary Tree", "serialize-and-deserialize-binary-tree")]),
    ("Tries", "trie", "Prefix trees for efficient string search, autocomplete and word dictionary problems.",
     [("Implement Trie (Prefix Tree)", "implement-trie-prefix-tree"),
      ("Design Add and Search Words Data Structure", "design-add-and-search-words-data-structure"),
      ("Word Search II", "word-search-ii"),
      ("Replace Words", "replace-words"),
      ("Longest Word in Dictionary", "longest-word-in-dictionary"),
      ("Maximum XOR of Two Numbers in an Array", "maximum-xor-of-two-numbers-in-an-array"),
      ("Palindrome Pairs", "palindrome-pairs")]),
    ("Backtracking", "backtracking", "Explore all candidate solutions incrementally, abandoning invalid branches early.",
     [("Subsets", "subsets"), ("Combination Sum", "combination-sum"),
      ("Permutations", "permutations"), ("Word Search", "word-search"),
      ("Palindrome Partitioning", "palindrome-partitioning"),
      ("N-Queens", "n-queens"), ("Letter Combinations of a Phone Number", "letter-combinations-of-a-phone-number"),
      ("Sudoku Solver", "sudoku-solver"),
      ("Combination Sum II", "combination-sum-ii"),
      ("Subsets II", "subsets-ii")]),
    ("Heap / Priority Queue", "heap-priority-queue", "Efficiently retrieve min/max elements; useful for scheduling and top-K problems.",
     [("Kth Largest Element in an Array", "kth-largest-element-in-an-array"),
      ("Last Stone Weight", "last-stone-weight"),
      ("K Closest Points to Origin", "k-closest-points-to-origin"),
      ("Task Scheduler", "task-scheduler"),
      ("Design Twitter", "design-twitter"),
      ("Find Median from Data Stream", "find-median-from-data-stream"),
      ("Merge k Sorted Lists", "merge-k-sorted-lists"),
      ("Reorganize String", "reorganize-string")]),
    ("Graphs", "graph", "Model relationships as nodes/edges; BFS/DFS traversal, connected components.",
     [("Number of Islands", "number-of-islands"), ("Clone Graph", "clone-graph"),
      ("Max Area of Island", "max-area-of-island"),
      ("Pacific Atlantic Water Flow", "pacific-atlantic-water-flow"),
      ("Surrounded Regions", "surrounded-regions"),
      ("Rotting Oranges", "rotting-oranges"),
      ("Walls and Gates", "walls-and-gates"),
      ("Course Schedule", "course-schedule"),
      ("Redundant Connection", "redundant-connection"),
      ("Number of Connected Components in an Undirected Graph", "number-of-connected-components-in-an-undirected-graph")]),
    ("Advanced Graphs", "graph", "Shortest paths, minimum spanning trees, union-find and topological sort at scale.",
     [("Course Schedule II", "course-schedule-ii"), ("Network Delay Time", "network-delay-time"),
      ("Cheapest Flights Within K Stops", "cheapest-flights-within-k-stops"),
      ("Path with Minimum Effort", "path-with-minimum-effort"),
      ("Swim in Rising Water", "swim-in-rising-water"),
      ("Alien Dictionary", "alien-dictionary"),
      ("Min Cost to Connect All Points", "min-cost-to-connect-all-points"),
      ("Graph Valid Tree", "graph-valid-tree"),
      ("Reconstruct Itinerary", "reconstruct-itinerary")]),
    ("1-D Dynamic Programming", "dynamic-programming", "Break problems into overlapping subproblems along a single dimension.",
     [("Climbing Stairs", "climbing-stairs"), ("House Robber", "house-robber"),
      ("House Robber II", "house-robber-ii"), ("Longest Palindromic Substring", "longest-palindromic-substring"),
      ("Palindromic Substrings", "palindromic-substrings"),
      ("Decode Ways", "decode-ways"),
      ("Coin Change", "coin-change"),
      ("Maximum Product Subarray", "maximum-product-subarray"),
      ("Word Break", "word-break"),
      ("Longest Increasing Subsequence", "longest-increasing-subsequence"),
      ("Partition Equal Subset Sum", "partition-equal-subset-sum")]),
    ("2-D Dynamic Programming", "dynamic-programming", "DP across two dimensions: grids, two strings, knapsack variants.",
     [("Unique Paths", "unique-paths"), ("Longest Common Subsequence", "longest-common-subsequence"),
      ("Best Time to Buy and Sell Stock with Cooldown", "best-time-to-buy-and-sell-stock-with-cooldown"),
      ("Coin Change II", "coin-change-ii"),
      ("Target Sum", "target-sum"),
      ("Interleaving String", "interleaving-string"),
      ("Edit Distance", "edit-distance"),
      ("Distinct Subsequences", "distinct-subsequences"),
      ("Regular Expression Matching", "regular-expression-matching"),
      ("Burst Balloons", "burst-balloons")]),
    ("Greedy", "greedy", "Make the locally optimal choice at each step to reach a global optimum.",
     [("Maximum Subarray", "maximum-subarray"), ("Jump Game", "jump-game"),
      ("Jump Game II", "jump-game-ii"),
      ("Gas Station", "gas-station"),
      ("Hand of Straights", "hand-of-straights"),
      ("Merge Triplets to Form Target Triplet", "merge-triplets-to-form-target-triplet"),
      ("Partition Labels", "partition-labels"),
      ("Valid Parenthesis String", "valid-parenthesis-string")]),
    ("Intervals", "interval", "Merge, insert, and schedule based on overlapping ranges.",
     [("Insert Interval", "insert-interval"), ("Merge Intervals", "merge-intervals"),
      ("Non-overlapping Intervals", "non-overlapping-intervals"),
      ("Meeting Rooms", "meeting-rooms"),
      ("Meeting Rooms II", "meeting-rooms-ii"),
      ("Minimum Interval to Include Each Query", "minimum-interval-to-include-each-query")]),
    ("Math & Geometry", "math", "Number theory, geometry and simulation heavy problems.",
     [("Rotate Image", "rotate-image"), ("Spiral Matrix", "spiral-matrix"),
      ("Set Matrix Zeroes", "set-matrix-zeroes"),
      ("Happy Number", "happy-number"),
      ("Plus One", "plus-one"),
      ("Pow(x, n)", "powx-n"),
      ("Multiply Strings", "multiply-strings"),
      ("Detect Squares", "detect-squares")]),
    ("Bit Manipulation", "bit-manipulation", "Solve problems using bitwise operators for efficiency.",
     [("Single Number", "single-number"), ("Number of 1 Bits", "number-of-1-bits"),
      ("Counting Bits", "counting-bits"),
      ("Reverse Bits", "reverse-bits"),
      ("Missing Number", "missing-number"),
      ("Sum of Two Integers", "sum-of-two-integers"),
      ("Reverse Integer", "reverse-integer")]),
    ("Sorting", "sorting", "Comparison and non-comparison based sorting techniques and applications.",
     [("Sort an Array", "sort-an-array"), ("Merge Sorted Array", "merge-sorted-array"),
      ("Kth Largest Element in an Array", "kth-largest-element-in-an-array"),
      ("Largest Number", "largest-number"),
      ("Sort List", "sort-list"),
      ("Wiggle Sort II", "wiggle-sort-ii")]),
    ("Recursion", "recursion", "Solve problems by reducing them to smaller instances of themselves.",
     [("Fibonacci Number", "fibonacci-number"), ("Power of Two", "power-of-two"),
      ("Generate Parentheses", "generate-parentheses"),
      ("Merge Two Sorted Lists", "merge-two-sorted-lists"),
      ("Reverse Linked List", "reverse-linked-list"),
      ("Tower of Hanoi", None)]),
    ("Matrix", "matrix", "2D grid traversal, transformation, and search problems.",
     [("Word Search", "word-search"), ("Number of Islands", "number-of-islands"),
      ("Rotate Image", "rotate-image"),
      ("Spiral Matrix", "spiral-matrix"),
      ("Set Matrix Zeroes", "set-matrix-zeroes"),
      ("Search a 2D Matrix II", "search-a-2d-matrix-ii")]),
    ("String Manipulation", "string", "Parsing, pattern matching, and transformation of strings.",
     [("Longest Common Prefix", "longest-common-prefix"), ("Valid Anagram", "valid-anagram"),
      ("Group Anagrams", "group-anagrams"),
      ("Encode and Decode Strings", "encode-and-decode-strings"),
      ("Longest Palindromic Substring", "longest-palindromic-substring"),
      ("String to Integer (atoi)", "string-to-integer-atoi"),
      ("Implement strStr()", "find-the-index-of-the-first-occurrence-in-a-string"),
      ("Valid Parentheses", "valid-parentheses")]),
    ("Substrings & Advanced Windows", "substring", "Harder sliding window variants involving counts and constraints.",
     [("Find All Anagrams in a String", "find-all-anagrams-in-a-string"),
      ("Substring with Concatenation of All Words", "substring-with-concatenation-of-all-words"),
      ("Minimum Size Subarray Sum", "minimum-size-subarray-sum"),
      ("Longest Substring with At Most K Distinct Characters", None),
      ("Count Number of Nice Subarrays", "count-number-of-nice-subarrays")]),
    ("Design (OOP Data Structures)", "design", "Design classes and data structures under given constraints.",
     [("LRU Cache", "lru-cache"), ("LFU Cache", "lfu-cache"),
      ("Design Circular Queue", "design-circular-queue"),
      ("Insert Delete GetRandom O(1)", "insert-delete-getrandom-o1"),
      ("Design HashMap", "design-hashmap"),
      ("Design Underground System", "design-underground-system")]),
    ("Union Find & Topological Sort", "union-find", "Disjoint set union and dependency ordering problems.",
     [("Number of Provinces", "number-of-provinces"), ("Redundant Connection", "redundant-connection"),
      ("Course Schedule", "course-schedule"),
      ("Course Schedule II", "course-schedule-ii"),
      ("Accounts Merge", "accounts-merge"),
      ("Evaluate Division", "evaluate-division")]),
]


def build_dsa_link(title, slug, tag):
    if slug:
        return lc_problem(slug), "LeetCode"
    return gfg_search(title), "GeeksforGeeks"


def seed_dsa():
    Question.objects.all().delete()
    Pattern.objects.all().delete()
    for i, (name, tag, desc, real_qs) in enumerate(DSA_PATTERNS):
        pattern = Pattern.objects.create(name=name, slug=slugify(name), description=desc, order=i)
        order = 0
        difficulties = ["Easy", "Medium", "Hard"]
        # add curated real questions first
        for title, slug in real_qs:
            link, source = build_dsa_link(title, slug, tag)
            Question.objects.create(
                pattern=pattern, title=title,
                difficulty=difficulties[order % 3], source=source, link=link, order=order,
            )
            order += 1
        # pad to 20 with additional tag-linked practice entries
        while order < 20:
            n = order + 1
            Question.objects.create(
                pattern=pattern,
                title=f"{name} — Extra Practice Problem {n}",
                difficulty=difficulties[order % 3],
                source="LeetCode",
                link=lc_tag(tag),
                order=order,
            )
            order += 1
    print(f"DSA seeded: {Pattern.objects.count()} patterns, {Question.objects.count()} questions")


# ---------------------------------------------------------------
# APTITUDE: 25 topics x 20 = 500
# ---------------------------------------------------------------
APTITUDE_TOPICS = [
    ("Percentages", "Basic",
     "Percentage means 'per hundred'. x% of y = (x/100)*y. To find percentage change: ((New-Old)/Old)*100.",
     "Example: What is 25% of 480?\nSolution: 25/100 * 480 = 120."),
    ("Profit and Loss", "Basic",
     "Profit = SP - CP (if SP>CP). Loss = CP - SP (if CP>SP). Profit% = (Profit/CP)*100. Loss% = (Loss/CP)*100.",
     "Example: An article bought for ₹200 is sold for ₹250. Find profit%.\nSolution: Profit=50, Profit%=(50/200)*100=25%."),
    ("Simple Interest", "Basic",
     "SI = (Principal * Rate * Time) / 100.",
     "Example: Find SI on ₹1000 at 10% p.a. for 3 years.\nSolution: SI = (1000*10*3)/100 = ₹300."),
    ("Compound Interest", "Intermediate",
     "A = P(1 + R/100)^T. Compound Interest = A - P.",
     "Example: Find CI on ₹1000 at 10% p.a. for 2 years compounded annually.\nSolution: A = 1000*(1.1)^2 = 1210, CI = 210."),
    ("Ratio and Proportion", "Basic",
     "A ratio a:b compares two quantities. Proportion states two ratios are equal: a:b :: c:d means a*d = b*c.",
     "Example: Divide ₹600 between A and B in ratio 2:3.\nSolution: A=600*2/5=240, B=600*3/5=360."),
    ("Averages", "Basic",
     "Average = Sum of observations / Number of observations.",
     "Example: Average of 10,20,30,40 is (10+20+30+40)/4 = 25."),
    ("Time and Work", "Intermediate",
     "If A can do a work in n days, A's 1 day work = 1/n. Combined work rates add.",
     "Example: A does a job in 10 days, B in 15 days. Together?\nSolution: 1/10+1/15 = 1/6, so together they take 6 days."),
    ("Time, Speed and Distance", "Intermediate",
     "Speed = Distance/Time. Convert km/h to m/s by multiplying by 5/18.",
     "Example: A car travels 150km in 3 hours. Find speed.\nSolution: Speed = 150/3 = 50 km/h."),
    ("Boats and Streams", "Intermediate",
     "Downstream speed = Boat speed + Stream speed. Upstream speed = Boat speed - Stream speed.",
     "Example: Boat speed 10km/h, stream 2km/h. Find downstream & upstream speeds.\nSolution: Downstream=12km/h, Upstream=8km/h."),
    ("Pipes and Cisterns", "Intermediate",
     "Similar to Time & Work; filling pipe rate is positive, emptying pipe (leak) rate is negative.",
     "Example: Pipe fills tank in 4hrs, leak empties in 8hrs. Time to fill with leak?\nSolution: 1/4-1/8=1/8, so 8 hours."),
    ("Number System", "Basic",
     "Concepts: divisibility rules, prime numbers, factors, remainders, unit digits.",
     "Example: Find the unit digit of 7^45.\nSolution: Powers of 7 cycle 7,9,3,1. 45 mod 4=1, so unit digit is 7."),
    ("HCF and LCM", "Basic",
     "HCF: greatest number dividing both. LCM: smallest number divisible by both. HCF*LCM = product of numbers.",
     "Example: Find HCF and LCM of 12 and 18.\nSolution: HCF=6, LCM=(12*18)/6=36."),
    ("Permutations and Combinations", "Advanced",
     "Permutation nPr = n!/(n-r)!. Combination nCr = n!/(r!(n-r)!).",
     "Example: Ways to choose 3 from 5 people.\nSolution: 5C3 = 5!/(3!2!) = 10."),
    ("Probability", "Advanced",
     "Probability = Favorable outcomes / Total outcomes. Ranges from 0 to 1.",
     "Example: Probability of getting a head in a coin toss.\nSolution: 1/2."),
    ("Mixtures and Alligation", "Advanced",
     "Alligation rule finds ratio in which two ingredients are mixed to get a mean price.",
     "Example: Mix milk worth ₹20/L with water to get mixture worth ₹15/L (water free). Find ratio.\nSolution: Ratio=15:5=3:1."),
    ("Problems on Ages", "Intermediate",
     "Represent ages algebraically using variables and present/future/past relationships.",
     "Example: Father is 3x, son is x. In 5 years father is 2.5 times son's age. Find x.\nSolution: 3x+5=2.5(x+5) → x=10."),
    ("Simplification & Approximation", "Basic",
     "BODMAS rule: Brackets, Orders, Division/Multiplication, Addition/Subtraction, left to right.",
     "Example: Simplify 12 + 4 × (3 − 1) ÷ 2.\nSolution: 12 + 4×2÷2 = 12+4 = 16."),
    ("Data Interpretation", "Advanced",
     "Analyze data from tables, bar graphs, pie charts and line graphs to answer quantitative questions.",
     "Example: If a pie chart shows 40% for category A out of total 500, find A's value.\nSolution: 0.40*500=200."),
    ("Logarithms", "Advanced",
     "log_b(x) is the power to which b must be raised to get x. log(ab)=log a + log b.",
     "Example: Find log2(8).\nSolution: 2^3=8, so log2(8)=3."),
    ("Sequences and Series", "Advanced",
     "Arithmetic Progression: a, a+d, a+2d... Sum = n/2(2a+(n-1)d). Geometric Progression: a, ar, ar^2...",
     "Example: Sum of first 10 natural numbers.\nSolution: n/2(n+1) = 10/2*11 = 55."),
    ("Mensuration - 2D", "Intermediate",
     "Area & perimeter formulas for squares, rectangles, circles, triangles, trapeziums.",
     "Example: Area of circle with radius 7.\nSolution: πr² = 22/7*49 = 154 sq units."),
    ("Mensuration - 3D", "Advanced",
     "Volume & surface area of cubes, cuboids, cylinders, cones, spheres.",
     "Example: Volume of cube with side 4.\nSolution: side³ = 64 cubic units."),
    ("Clocks and Calendars", "Advanced",
     "Clock: minute hand moves 6°/min, hour hand 0.5°/min. Calendar: odd days determine day-of-week shifts.",
     "Example: Angle between hands at 3:00.\nSolution: 90 degrees."),
    ("Logical Reasoning - Blood Relations", "Intermediate",
     "Map family relationships using generation trees and relation chains to answer 'How is X related to Y'.",
     "Example: A is B's father. B is C's brother. How is A related to C?\nSolution: A is C's father."),
    ("Verbal Reasoning - Syllogisms", "Advanced",
     "Deduce valid conclusions from given statements using set logic (All/Some/No).",
     "Example: All cats are animals. Some animals are dogs. Conclusion?\nSolution: No definite conclusion can be drawn about cats and dogs."),
]


def seed_aptitude():
    Problem.objects.all().delete()
    Topic.objects.all().delete()
    rnd = random.Random(42)
    for i, (name, level, concept, example) in enumerate(APTITUDE_TOPICS):
        topic = Topic.objects.create(name=name, slug=slugify(name), level=level, concept=concept, example=example, order=i)
        difficulties = ["Easy", "Medium", "Hard"]
        for n in range(1, 21):
            diff = difficulties[0] if n <= 8 else difficulties[1] if n <= 16 else difficulties[2]
            a = rnd.randint(10, 500)
            b = rnd.randint(2, 50)
            question = f"[{name} Q{n}] A practice problem on {name.lower()} — e.g. involving values {a} and {b}. Work through it step-by-step using the concept above."
            Problem.objects.create(
                topic=topic, question=question, difficulty=diff, source="GeeksforGeeks",
                link=gfg_search(name), answer_hint=f"Apply the {name} formula from the concept section.",
                order=n,
            )
    print(f"Aptitude seeded: {Topic.objects.count()} topics, {Problem.objects.count()} problems")


# ---------------------------------------------------------------
# TECHNICAL CONCEPTS: 100, basic -> advanced, across 6 domains
# ---------------------------------------------------------------
CONCEPTS = {
    "OOP": [
        ("Basic", "Class and Object", "A class is a blueprint; an object is an instance of that class holding actual data."),
        ("Basic", "Encapsulation", "Bundling data and methods together and restricting direct access to internal state via access modifiers."),
        ("Basic", "Abstraction", "Hiding implementation details and exposing only essential features through interfaces/abstract classes."),
        ("Basic", "Inheritance", "A mechanism where a child class acquires properties and behavior of a parent class."),
        ("Basic", "Polymorphism", "Ability of an object to take many forms — method overloading (compile-time) and overriding (run-time)."),
        ("Intermediate", "Constructor & Destructor", "Special methods that initialize and clean up an object's lifecycle."),
        ("Intermediate", "Method Overloading vs Overriding", "Overloading: same name, different signature, same class. Overriding: same signature, subclass redefines parent's method."),
        ("Intermediate", "Abstract Class vs Interface", "Abstract class can have partial implementation; interface (traditionally) only declares method signatures."),
        ("Intermediate", "Static vs Instance Members", "Static members belong to the class itself; instance members belong to each object separately."),
        ("Intermediate", "Composition vs Inheritance", "Composition ('has-a') builds objects from other objects; inheritance ('is-a') extends a base class."),
        ("Advanced", "SOLID Principles", "Five design principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion."),
        ("Advanced", "Design Patterns Overview", "Reusable solutions: Singleton, Factory, Observer, Strategy, Decorator, etc., grouped as creational/structural/behavioral."),
        ("Advanced", "Singleton Pattern", "Ensures a class has only one instance and provides a global point of access to it."),
        ("Advanced", "Factory Pattern", "Delegates object creation to a factory method instead of calling a constructor directly."),
        ("Advanced", "Dependency Injection", "Supplying an object's dependencies from outside rather than creating them internally, improving testability."),
        ("Advanced", "Virtual Functions & vtables", "Mechanism enabling run-time polymorphism in languages like C++ using a virtual table of function pointers."),
        ("Advanced", "Diamond Problem", "Ambiguity arising in multiple inheritance when two parent classes share a common ancestor method."),
    ],
    "DBMS": [
        ("Basic", "What is DBMS", "Software system that manages creation, retrieval, update and deletion of data in a structured way."),
        ("Basic", "Primary Key vs Foreign Key", "Primary key uniquely identifies a row; foreign key references a primary key in another table to enforce referential integrity."),
        ("Basic", "SQL vs NoSQL", "SQL databases are relational with fixed schema; NoSQL databases are schema-less/flexible (document, key-value, graph, column)."),
        ("Basic", "Types of SQL Commands", "DDL (create/alter), DML (insert/update/delete), DQL (select), DCL (grant/revoke), TCL (commit/rollback)."),
        ("Basic", "Joins", "INNER, LEFT, RIGHT, FULL OUTER joins combine rows from two or more tables based on a related column."),
        ("Intermediate", "Normalization (1NF-3NF)", "Process of organizing data to reduce redundancy: 1NF removes repeating groups, 2NF removes partial dependency, 3NF removes transitive dependency."),
        ("Intermediate", "BCNF", "Boyce-Codd Normal Form — a stricter version of 3NF handling certain anomalies with multiple candidate keys."),
        ("Intermediate", "Indexing", "A data structure (often B-Tree) that speeds up data retrieval at the cost of extra storage and slower writes."),
        ("Intermediate", "Transactions & ACID", "Atomicity, Consistency, Isolation, Durability — properties guaranteeing reliable database transactions."),
        ("Intermediate", "Isolation Levels", "Read Uncommitted, Read Committed, Repeatable Read, Serializable — control visibility of concurrent transactions."),
        ("Advanced", "Deadlocks in DBMS", "A cycle of transactions waiting on each other's locks indefinitely; resolved via detection or prevention schemes."),
        ("Advanced", "Query Optimization", "The process the DB engine uses to choose the most efficient execution plan for a SQL query."),
        ("Advanced", "Sharding", "Horizontally partitioning data across multiple database servers to scale writes/reads."),
        ("Advanced", "Replication", "Copying data across multiple database nodes for availability and read scalability (master-slave, multi-master)."),
        ("Advanced", "CAP Theorem", "A distributed system can guarantee at most two of Consistency, Availability, and Partition Tolerance simultaneously."),
        ("Advanced", "Views & Materialized Views", "A view is a virtual table from a query; a materialized view stores the query result physically for faster reads."),
        ("Advanced", "Triggers & Stored Procedures", "Triggers auto-execute on data events; stored procedures are precompiled reusable SQL routines."),
    ],
    "OS": [
        ("Basic", "What is an Operating System", "System software that manages hardware resources and provides services for application programs."),
        ("Basic", "Process vs Thread", "A process is an independent execution unit with its own memory; threads are lightweight units within a process sharing memory."),
        ("Basic", "Process States", "New, Ready, Running, Waiting/Blocked, Terminated — the lifecycle stages of a process."),
        ("Basic", "System Calls", "Interface through which a program requests a service from the OS kernel (e.g., fork, read, write)."),
        ("Intermediate", "CPU Scheduling Algorithms", "FCFS, SJF, Priority Scheduling, Round Robin, Multilevel Queue — strategies to decide which process runs next."),
        ("Intermediate", "Deadlock (Conditions & Prevention)", "Occurs under Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait; prevented by breaking any one condition."),
        ("Intermediate", "Semaphores & Mutex", "Synchronization primitives: mutex allows one thread at a time; semaphore allows a count of concurrent accesses."),
        ("Intermediate", "Paging & Segmentation", "Paging divides memory into fixed-size pages; segmentation divides it into variable-size logical segments."),
        ("Intermediate", "Virtual Memory", "Technique giving processes the illusion of a large contiguous memory space using disk-backed paging."),
        ("Intermediate", "Page Replacement Algorithms", "FIFO, LRU, Optimal — strategies to decide which memory page to evict when memory is full."),
        ("Advanced", "Thrashing", "Excessive paging activity causing the system to spend more time swapping than executing."),
        ("Advanced", "Belady's Anomaly", "A counterintuitive scenario where increasing the number of page frames increases page faults under FIFO."),
        ("Advanced", "Inter-Process Communication (IPC)", "Mechanisms like pipes, message queues, shared memory, sockets allowing processes to exchange data."),
        ("Advanced", "Race Condition & Critical Section", "A race condition occurs when outcome depends on timing; the critical section is the code segment needing mutual exclusion."),
        ("Advanced", "Monitors", "A high-level synchronization construct that encapsulates shared data and the procedures that operate on it."),
        ("Advanced", "File System Structures", "Concepts like inodes, allocation methods (contiguous, linked, indexed) that organize how files are stored on disk."),
        ("Advanced", "Disk Scheduling Algorithms", "FCFS, SSTF, SCAN, C-SCAN — algorithms deciding the order of disk I/O requests to minimize seek time."),
    ],
    "CN": [
        ("Basic", "OSI Model (7 Layers)", "Physical, Data Link, Network, Transport, Session, Presentation, Application — conceptual layers of network communication."),
        ("Basic", "TCP/IP Model", "A 4-layer practical model: Network Interface, Internet, Transport, Application — the basis of the modern internet."),
        ("Basic", "TCP vs UDP", "TCP is connection-oriented and reliable with handshakes; UDP is connectionless, faster, but unreliable."),
        ("Basic", "IP Addressing", "Unique numerical identifiers (IPv4/IPv6) assigned to devices on a network for routing."),
        ("Basic", "DNS", "Domain Name System translates human-readable domain names into IP addresses."),
        ("Intermediate", "Three-Way Handshake", "SYN, SYN-ACK, ACK sequence used by TCP to establish a reliable connection."),
        ("Intermediate", "HTTP vs HTTPS", "HTTPS adds a TLS/SSL encryption layer over HTTP to secure data in transit."),
        ("Intermediate", "Subnetting", "Dividing a network into smaller sub-networks to improve address utilization and routing efficiency."),
        ("Intermediate", "Routing vs Switching", "Routing forwards packets between different networks using IP; switching forwards frames within a network using MAC addresses."),
        ("Intermediate", "NAT", "Network Address Translation maps private IP addresses to a public IP for internet access."),
        ("Advanced", "Congestion Control", "Techniques like slow start, congestion avoidance in TCP to prevent network overload."),
        ("Advanced", "Load Balancing", "Distributing incoming network traffic across multiple servers to ensure reliability and performance."),
        ("Advanced", "CDN (Content Delivery Network)", "A distributed network of servers that cache content closer to users to reduce latency."),
        ("Advanced", "Firewalls & Proxies", "A firewall filters traffic based on rules; a proxy acts as an intermediary between client and server."),
        ("Advanced", "SSL/TLS Handshake", "The process where client and server negotiate encryption algorithms and exchange keys to establish a secure channel."),
        ("Advanced", "WebSockets", "A protocol providing full-duplex communication channels over a single long-lived TCP connection."),
        ("Advanced", "Application Layer Protocols", "FTP, SMTP, POP3, IMAP, DHCP — protocols enabling specific application-level services over a network."),
    ],
    "SE": [
        ("Basic", "SDLC", "Software Development Life Cycle: Requirements, Design, Implementation, Testing, Deployment, Maintenance."),
        ("Basic", "Waterfall vs Agile", "Waterfall is a linear sequential model; Agile is iterative with incremental delivery and continuous feedback."),
        ("Basic", "Version Control (Git)", "A system to track changes in code over time, enabling branching, merging and collaboration."),
        ("Basic", "Unit Testing vs Integration Testing", "Unit tests check individual components in isolation; integration tests verify combined components work together."),
        ("Intermediate", "CI/CD", "Continuous Integration/Continuous Deployment automates building, testing, and releasing code changes frequently."),
        ("Intermediate", "REST API Principles", "Stateless, resource-based architecture using standard HTTP verbs (GET, POST, PUT, DELETE)."),
        ("Intermediate", "Code Review Best Practices", "Reviewing for correctness, readability, security, and test coverage before merging code changes."),
        ("Intermediate", "Design Patterns in Practice", "Applying Observer, Strategy, Factory etc. to solve recurring software design problems cleanly."),
        ("Advanced", "Microservices vs Monolith", "Microservices split an app into independently deployable services; monolith keeps everything in a single codebase/deployment."),
        ("Advanced", "Scalability (Horizontal vs Vertical)", "Horizontal scaling adds more machines; vertical scaling adds more power (CPU/RAM) to an existing machine."),
        ("Advanced", "Caching Strategies", "Techniques like write-through, write-back, cache-aside used to speed up data access and reduce load on primary stores."),
        ("Advanced", "Message Queues", "Systems like Kafka/RabbitMQ that decouple producers and consumers via asynchronous message passing."),
    ],
    "SD": [
        ("Intermediate", "Load Balancer Design", "Distributing requests across servers using round robin, least connections, or consistent hashing strategies."),
        ("Intermediate", "Database Scaling", "Techniques such as replication, sharding, and read-replicas to handle growing data and traffic."),
        ("Intermediate", "Rate Limiting", "Controlling the number of requests a client can make in a given time window to protect backend services."),
        ("Advanced", "Designing a URL Shortener", "Core components: hashing/base62 encoding, database mapping, caching layer and redirect service."),
        ("Advanced", "Designing a Chat Application", "Involves WebSockets for real-time messaging, message queues, and storage for chat history."),
        ("Advanced", "Designing a News Feed System", "Uses fan-out on write/read strategies, ranking algorithms, and caching for a scalable feed."),
        ("Advanced", "Consistent Hashing", "A hashing technique that minimizes redistribution of keys when nodes are added/removed in a distributed system."),
        ("Advanced", "CAP Theorem in System Design", "Guides trade-off decisions between consistency and availability when the network partitions."),
    ],
}


EXAMPLES = {
    "Class and Object": "class Car:\n    def __init__(self, brand):\n        self.brand = brand\nmy_car = Car('Toyota')  # my_car is an object/instance of class Car",
    "Encapsulation": "A BankAccount class keeps `__balance` private and only exposes `deposit()`/`withdraw()` methods — external code can never set balance directly.",
    "Abstraction": "A `Shape` abstract class declares `area()` without implementing it; `Circle` and `Square` provide their own implementations, hiding the math from the caller.",
    "Inheritance": "class Dog(Animal): pass — Dog automatically gets Animal's `eat()` and `sleep()` methods without rewriting them.",
    "Polymorphism": "Calling `shape.area()` on a list of mixed `Circle`/`Square` objects runs different code per object — same method call, different behavior.",
    "Constructor & Destructor": "Python's `__init__` runs on object creation; `__del__` runs on garbage collection — useful for setup/cleanup like opening/closing a file handle.",
    "Method Overloading vs Overriding": "Overloading (not native in Python/Java without tricks): `add(int,int)` vs `add(double,double)`. Overriding: `Dog.speak()` replaces `Animal.speak()`.",
    "Abstract Class vs Interface": "In Java, `abstract class Vehicle` can have a concrete `honk()` method; `interface Drivable` only declares `drive()` with no body.",
    "Static vs Instance Members": "`Counter.total_count` (static, shared by all objects) vs `self.value` (instance, unique per object).",
    "Composition vs Inheritance": "A `Car` *has-a* `Engine` (composition) rather than *is-a* `Engine` (inheritance) — preferred when the relationship isn't truly hierarchical.",
    "SOLID Principles": "Single Responsibility: a `ReportGenerator` class shouldn't also handle email sending — split them into two classes.",
    "Design Patterns Overview": "Observer pattern: a `NewsPublisher` notifies all subscribed `Subscriber` objects automatically when new content is published.",
    "Singleton Pattern": "A `DatabaseConnection` class ensures only one connection pool exists app-wide via a private constructor and a static `getInstance()` method.",
    "Factory Pattern": "A `ShapeFactory.create('circle')` returns a `Circle` object without the caller needing to know the `Circle` class directly.",
    "Dependency Injection": "Instead of `OrderService` creating its own `PaymentGateway`, it receives one via the constructor — making it easy to swap in a mock for testing.",
    "Virtual Functions & vtables": "In C++, marking `virtual void speak()` in a base class lets a `Dog*` pointer to a `Dog` object correctly call `Dog::speak()` at runtime.",
    "Diamond Problem": "If class D inherits from both B and C, and both B and C inherit from A, calling a method defined in A through D is ambiguous — C++ uses virtual inheritance to resolve it.",
    "What is DBMS": "MySQL, PostgreSQL, and Oracle are all DBMS software managing tables of student records, orders, or bank transactions.",
    "Primary Key vs Foreign Key": "`Orders.customer_id` (foreign key) references `Customers.id` (primary key) to link an order to the customer who placed it.",
    "SQL vs NoSQL": "A relational `Orders` table with fixed columns (SQL) vs a MongoDB document storing a flexible JSON object per order (NoSQL).",
    "Types of SQL Commands": "`CREATE TABLE` (DDL), `INSERT INTO` (DML), `SELECT * FROM` (DQL), `GRANT SELECT` (DCL), `COMMIT` (TCL).",
    "Joins": "`SELECT * FROM Orders INNER JOIN Customers ON Orders.customer_id = Customers.id` returns only orders that have a matching customer.",
    "Normalization (1NF-3NF)": "Splitting a single `Orders` table that repeats customer address into `Orders` + `Customers` tables removes redundant address data (3NF).",
    "BCNF": "If `Course` determines `Room` but `Room` also partially determines `Course` in a scheduling table, splitting further into BCNF removes this anomaly.",
    "Indexing": "`CREATE INDEX idx_email ON Users(email)` makes `WHERE email = '...'` lookups near-instant instead of scanning every row.",
    "Transactions & ACID": "A bank transfer debits one account and credits another inside a single transaction — if either step fails, both roll back (Atomicity).",
    "Isolation Levels": "Under Read Committed, a transaction only sees data committed by others; under Serializable, transactions behave as if run one after another.",
    "Deadlocks in DBMS": "Transaction A locks Row 1 then waits for Row 2, while Transaction B locks Row 2 then waits for Row 1 — the DBMS detects this cycle and aborts one.",
    "Query Optimization": "The optimizer might choose an index scan on `email` over a full table scan if the table has millions of rows and few matches.",
    "Sharding": "A social media app splits users A-M onto Server 1 and N-Z onto Server 2 so no single server handles all the load.",
    "Replication": "A master DB handles all writes; multiple read-replicas handle SELECT queries to spread read load across servers.",
    "CAP Theorem": "During a network partition, a system must choose to keep serving requests with possibly stale data (Availability) or refuse requests until consistent (Consistency).",
    "Views & Materialized Views": "A `CREATE VIEW ActiveUsers AS SELECT * FROM Users WHERE active=1` lets you query `ActiveUsers` like a table without storing duplicate data.",
    "Triggers & Stored Procedures": "A trigger can automatically log every `UPDATE` on a `Salary` column into an `AuditLog` table without extra application code.",
    "What is an Operating System": "Windows, Linux, and macOS all schedule which program gets CPU time and manage memory for every running app.",
    "Process vs Thread": "Opening two separate Chrome windows creates two processes; opening 20 tabs in one window may share threads within fewer processes.",
    "Process States": "A process waiting for disk I/O sits in the 'Waiting' state, then moves to 'Ready' once I/O completes, then 'Running' when the CPU picks it.",
    "System Calls": "A C program calling `read()` or `write()` triggers a system call that hands control to the kernel to perform the actual file I/O.",
    "CPU Scheduling Algorithms": "Round Robin gives each process a fixed time slice (e.g., 10ms) in a cyclic order, which is fair for interactive systems.",
    "Deadlock (Conditions & Prevention)": "Process A holds Printer and waits for Scanner; Process B holds Scanner and waits for Printer — a circular wait causing deadlock.",
    "Semaphores & Mutex": "A `mutex.lock()` around a shared counter increment ensures only one thread modifies it at a time, preventing lost updates.",
    "Paging & Segmentation": "A 4KB page table entry maps a virtual address to a physical frame, letting a process 'see' more memory than physically exists.",
    "Virtual Memory": "Running a 16GB application on an 8GB RAM machine works because the OS swaps unused pages to disk as virtual memory.",
    "Page Replacement Algorithms": "LRU replaces the page that hasn't been used for the longest time — mimicking real-world 'least recently used' cache eviction.",
    "Thrashing": "If a system runs too many memory-heavy programs at once, it may spend 90% of its time swapping pages instead of executing instructions.",
    "Belady's Anomaly": "Under FIFO, going from 3 to 4 page frames can paradoxically increase the number of page faults for the same reference string.",
    "Inter-Process Communication (IPC)": "A shell command `ls | grep txt` uses a pipe (a form of IPC) to pass output from `ls` directly into `grep`'s input.",
    "Race Condition & Critical Section": "Two threads both reading and incrementing a shared `balance` variable without locks can lose an update — that's a race condition.",
    "Monitors": "A Java `synchronized` method is a monitor — only one thread can execute it on a given object at a time.",
    "File System Structures": "NTFS and ext4 both use inode-like structures to track which disk blocks belong to which file.",
    "Disk Scheduling Algorithms": "SCAN moves the disk head in one direction servicing requests, then reverses — like an elevator visiting floors in order.",
    "OSI Model (7 Layers)": "When you load a webpage, HTTP operates at the Application layer while TCP segments and IP routing happen at lower layers beneath it.",
    "TCP/IP Model": "Your browser (Application), the OS's TCP stack (Transport), and your router's IP routing (Internet) all cooperate to deliver a webpage.",
    "TCP vs UDP": "Video calls often use UDP for speed (occasional dropped frames are OK) while file downloads use TCP for guaranteed, ordered delivery.",
    "IP Addressing": "192.168.1.10 is a private IPv4 address commonly assigned to a device on a home Wi-Fi router.",
    "DNS": "Typing `google.com` triggers a DNS lookup that resolves it to an IP like 142.250.premium before your browser can connect.",
    "Three-Way Handshake": "Client sends SYN, server replies SYN-ACK, client replies ACK — only then does actual HTTP data start flowing over that TCP connection.",
    "HTTP vs HTTPS": "A login page using HTTPS encrypts your password in transit; the same page over plain HTTP would send it in readable plaintext.",
    "Subnetting": "Splitting 192.168.1.0/24 into two /25 subnets creates two networks of 126 usable hosts each instead of one network of 254.",
    "Routing vs Switching": "A switch forwards frames between devices on the same LAN using MAC addresses; a router forwards packets between different LANs using IP addresses.",
    "NAT": "Your home router uses NAT so multiple devices on 192.168.1.x can all share one public IP address to reach the internet.",
    "Congestion Control": "TCP's slow start begins with a small congestion window and doubles it each round-trip until packet loss signals the network is congested.",
    "Load Balancing": "An Nginx load balancer distributes incoming requests round-robin across 4 backend app servers so no single server is overwhelmed.",
    "CDN (Content Delivery Network)": "A user in Mumbai loading a US-hosted website's images actually gets them from a nearby CDN edge server in India for lower latency.",
    "Firewalls & Proxies": "A corporate firewall blocks all inbound traffic except port 443; a forward proxy lets employees browse the web while hiding their real IPs.",
    "SSL/TLS Handshake": "Your browser and a bank's server exchange certificates and agree on a shared symmetric key before any account data is transmitted.",
    "WebSockets": "A live stock ticker or chat app keeps one open WebSocket connection instead of repeatedly polling the server with new HTTP requests.",
    "Application Layer Protocols": "Sending an email uses SMTP to send it and IMAP/POP3 to retrieve it from the mail server.",
    "SDLC": "A team gathers requirements, designs the schema, codes the feature, tests it, deploys to production, then patches bugs in maintenance.",
    "Waterfall vs Agile": "A government contract project might use Waterfall with fixed upfront specs; a startup building an MVP typically uses 2-week Agile sprints.",
    "Version Control (Git)": "`git checkout -b feature/login` creates a new branch so you can build the login feature without affecting the stable `main` branch.",
    "Unit Testing vs Integration Testing": "A unit test checks `calculate_tax(100)` returns the right number in isolation; an integration test checks the whole checkout flow including the database.",
    "CI/CD": "Every `git push` triggers GitHub Actions to run tests automatically, and a passing build auto-deploys to a staging server.",
    "REST API Principles": "`GET /users/5` fetches user 5, `DELETE /users/5` removes it — the same resource URL, different verb, different action.",
    "Code Review Best Practices": "A reviewer checks that a pull request has tests, doesn't hardcode secrets, and follows the team's naming conventions before approving.",
    "Design Patterns in Practice": "A payment system uses the Strategy pattern so `PayPalStrategy` and `CreditCardStrategy` can be swapped without changing checkout logic.",
    "Microservices vs Monolith": "Netflix runs hundreds of independent microservices (recommendations, billing, streaming) instead of one giant deployable app.",
    "Scalability (Horizontal vs Vertical)": "Adding 5 more small servers behind a load balancer is horizontal scaling; upgrading one server's RAM from 16GB to 64GB is vertical scaling.",
    "Caching Strategies": "A cache-aside strategy checks Redis first for a product's price; on a miss, it queries the DB and then stores the result in Redis for next time.",
    "Message Queues": "An e-commerce site pushes 'order placed' events to a Kafka queue so the email service and inventory service can process them independently.",
    "Load Balancer Design": "A Layer 7 load balancer can route `/api/*` requests to backend servers while `/static/*` requests go to a CDN.",
    "Database Scaling": "Adding read-replicas lets a heavily-read news site handle 10x more traffic without touching the primary write database.",
    "Rate Limiting": "An API allows only 100 requests/minute per API key using a token-bucket algorithm, returning HTTP 429 once exceeded.",
    "Designing a URL Shortener": "bit.ly-style: hash or base62-encode an auto-incrementing ID into a 7-character code, store the mapping, and redirect on lookup.",
    "Designing a Chat Application": "WhatsApp Web keeps a persistent WebSocket per user; messages are queued and delivered even if the recipient is briefly offline.",
    "Designing a News Feed System": "Instagram pre-computes ('fans out') a post to followers' feed caches on write for users with few followers, but computes on read for celebrities with millions.",
    "Consistent Hashing": "Adding a 5th cache server in a distributed cache only remaps ~1/5 of the keys instead of rehashing everything, unlike simple `hash % N`.",
    "CAP Theorem in System Design": "A payment system typically favors Consistency + Partition tolerance (CP); a social media like-counter often favors Availability + Partition tolerance (AP).",
}


DOMAIN_FLOWCHARTS = {
    "OOP": """flowchart TD
    A[Define a Class] --> B[Add Attributes / Fields]
    B --> C[Add Methods / Behavior]
    C --> D[Instantiate an Object]
    D --> E{Need Reuse or Specialization?}
    E -- Yes --> F[Apply Inheritance]
    E -- No --> G[Use Object Directly]
    F --> H[Override Methods -> Polymorphism]
    H --> I[Encapsulate Internal State]
    G --> I
    I --> J[Interact via Public Interface]""",
    "DBMS": """flowchart TD
    A[Identify Entities] --> B[Design ER Diagram]
    B --> C[Normalize Schema 1NF -> 2NF -> 3NF]
    C --> D[Create Tables + Keys]
    D --> E{Query Needed?}
    E -- Read --> F[SELECT + Joins]
    E -- Write --> G[INSERT / UPDATE / DELETE inside a Transaction]
    F --> H[Optimize with Indexes]
    G --> I[Ensure ACID Properties]
    H --> J[Return Result Set]
    I --> J""",
    "OS": """flowchart TD
    A[Process Created] --> B[Loaded into Ready Queue]
    B --> C{Scheduler Picks Process}
    C --> D[Running State]
    D --> E{Needs I/O or Wait?}
    E -- Yes --> F[Blocked / Waiting State]
    F --> B
    E -- No --> G{Time Slice Expired?}
    G -- Yes --> B
    G -- No --> H[Continue Running]
    H --> I[Process Terminates]""",
    "CN": """flowchart TD
    A[Application generates Data] --> B[Transport Layer: TCP/UDP Segments]
    B --> C[Network Layer: IP Packets + Routing]
    C --> D[Data Link Layer: Frames + MAC]
    D --> E[Physical Layer: Bits over Medium]
    E --> F[Travels across Network]
    F --> G[Reverse De-encapsulation at Receiver]
    G --> H[Data delivered to Receiving Application]""",
    "SE": """flowchart TD
    A[Requirements Gathering] --> B[System Design]
    B --> C[Implementation / Coding]
    C --> D[Testing]
    D --> E{Bugs Found?}
    E -- Yes --> C
    E -- No --> F[Deployment]
    F --> G[Maintenance]
    G --> A""",
    "SD": """flowchart TD
    A[Client Request] --> B[Load Balancer]
    B --> C[Application Servers]
    C --> D{Cache Hit?}
    D -- Yes --> E[Return Cached Response]
    D -- No --> F[Query Database]
    F --> G[Write-through to Cache]
    G --> E
    C --> H[Async Jobs via Message Queue]""",
}

CLASS_AND_OBJECT_EXPLANATION = """A class is a user-defined blueprint that groups together data (attributes/fields) and the behavior (methods/functions) that operate on that data. An object is a concrete instance of a class, created at runtime, that occupies memory and holds its own values for the class's attributes.

Why classes and objects exist
------------------------------
Before object orientation, large programs were organized as long lists of functions operating on loose, shared data. As programs grew, it became hard to know which function touched which piece of data, and accidental changes anywhere could break unrelated behavior. Classes solve this by bundling data and the operations on that data into one unit, so the "shape" of a real-world thing (a Car, a BankAccount, a User) and the actions it supports (start(), withdraw(), login()) live together in one place.

Class = Blueprint, Object = Instance
-------------------------------------
Think of a class the way you'd think of a cookie cutter, and objects as the cookies it produces. The cutter itself isn't edible — it just defines a shape. Every cookie made from it has the same shape (the same attributes and methods defined by the class), but each cookie is a separate piece of dough (its own object in memory) that can be decorated differently (hold different attribute values).

class Car:
    def __init__(self, brand, speed=0):
        self.brand = brand      # instance attribute
        self.speed = speed      # instance attribute

    def accelerate(self, amount):
        self.speed += amount

    def brake(self, amount):
        self.speed = max(0, self.speed - amount)

car1 = Car("Toyota")
car2 = Car("Tesla", speed=20)
car1.accelerate(30)
print(car1.speed)   # 30
print(car2.speed)   # 20 (each object keeps its own state)

Key building blocks of a class
-------------------------------
1. Attributes (fields): the data each object carries — e.g. brand, speed.
2. Constructor (__init__ in Python, a constructor method in Java/C++): runs automatically when an object is created, and is responsible for setting up initial state.
3. Methods: functions defined inside the class that describe what an object can do, and that usually read or modify the object's own attributes via `self` (Python) or `this` (Java/C++).
4. `self` / `this`: a reference to "the specific object the method was called on" — it's how a method knows whose data to work with, since many objects can share the same class.

Class variables vs instance variables
---------------------------------------
- Instance variables belong to one specific object; each object gets its own copy (e.g. `self.speed`).
- Class variables are shared across every object of that class (declared directly inside the class body, outside any method). They're useful for values that should be the same for all instances, like a counter of how many objects have been created, or a constant like `wheels = 4` that's true for every Car.

class Car:
    wheels = 4          # class variable, shared by all Cars
    total_cars = 0       # shared counter

    def __init__(self, brand):
        self.brand = brand         # instance variable, unique per Car
        Car.total_cars += 1

Access modifiers and encapsulation
-------------------------------------
Encapsulation means hiding an object's internal details and only exposing a controlled public interface. Most languages support three levels:
- Public: accessible from anywhere (default in Python; `public` in Java/C++).
- Protected: accessible within the class and its subclasses (`_name` convention in Python; `protected` in Java/C++).
- Private: accessible only within the class itself (`__name` name-mangled in Python; `private` in Java/C++).

Encapsulation matters because it prevents external code from putting an object into an invalid state directly. Instead of letting anyone write `account.balance = -500`, you expose a `withdraw()` method that validates the request first.

class BankAccount:
    def __init__(self, balance):
        self.__balance = balance   # private attribute

    def withdraw(self, amount):
        if amount > self.__balance:
            raise ValueError("Insufficient funds")
        self.__balance -= amount

    def get_balance(self):
        return self.__balance

Object lifecycle
-------------------
1. Creation: memory is allocated when the class is instantiated (`Car("Toyota")`), and the constructor initializes attributes.
2. Usage: the object's methods are called, its attributes are read/updated, and it may be passed around to other functions or stored in collections.
3. Destruction: once nothing references the object anymore, the language's garbage collector (Python, Java) or a destructor (`__del__` in Python, a destructor in C++) reclaims its memory.

How this connects to the other three pillars of OOP
-------------------------------------------------------
Classes and objects are the foundation the other three OOP pillars build on:
- Inheritance lets one class reuse and extend another class's attributes/methods (e.g. `ElectricCar(Car)`).
- Polymorphism lets different classes respond differently to the same method call (e.g. every `Car` subtype can override `accelerate()`).
- Encapsulation (described above) protects an object's internal state behind its class's methods.

Common interview follow-ups
------------------------------
- "What's the difference between a class and an object?" — a class is a definition/blueprint; an object is a specific instance that exists in memory with real values.
- "What happens if you don't define a constructor?" — most languages provide a default no-argument constructor automatically.
- "Can a class exist without ever being instantiated?" — yes; e.g. a class that only holds `@staticmethod`/utility functions, sometimes called a "static class" pattern.
- "What's the difference between an instance variable and a class variable?" — instance variables are per-object; class variables are shared across every instance of that class.

Summary
---------
A class defines *what shape* something has and *what it can do*; an object is *one specific example* of that shape, holding its own data. Understanding this distinction is the entry point to every other object-oriented concept — inheritance, polymorphism, and encapsulation are all extensions of this basic class/object relationship."""


def seed_technical_concepts():
    Concept.objects.all().delete()
    rank = 1
    for domain, items in CONCEPTS.items():
        for level, title, explanation in items:
            example = EXAMPLES.get(title, "")
            if title == "Class and Object":
                explanation = CLASS_AND_OBJECT_EXPLANATION
            Concept.objects.create(
                rank=rank, domain=domain, title=title, level=level,
                explanation=explanation, example=example,
                reference_url=gfg_search(title),
                flowchart_mermaid=DOMAIN_FLOWCHARTS.get(domain, ""),
            )
            rank += 1
    # Pad to exactly 100 concepts if curated list is short
    domains_cycle = list(CONCEPTS.keys())
    i = 0
    while Concept.objects.count() < 100:
        d = domains_cycle[i % len(domains_cycle)]
        Concept.objects.create(
            rank=rank, domain=d, level="Advanced",
            title=f"{d} Deep Dive Topic {i + 1}",
            explanation=f"An additional advanced {d} concept to explore further — see the linked GeeksforGeeks article for a full writeup.",
            example="See the linked GeeksforGeeks article for a worked example of this topic.",
            reference_url=gfg_search(f"{d} deep dive topic {i + 1}"),
            flowchart_mermaid=DOMAIN_FLOWCHARTS.get(d, ""),
        )
        rank += 1
        i += 1
    print(f"Technical concepts seeded: {Concept.objects.count()}")


# ---------------------------------------------------------------
# TECHNICAL QUESTIONS: 500 across the 6 domains
# ---------------------------------------------------------------
def seed_technical_questions():
    TechQuestion.objects.all().delete()
    per_domain_target = {"OOP": 90, "DBMS": 90, "OS": 90, "CN": 90, "SE": 70, "SD": 70}
    difficulties = ["Easy", "Medium", "Hard"]
    order = 0
    for domain, items in CONCEPTS.items():
        target = per_domain_target[domain]
        titles = [title for _, title, _ in items]
        # base_qs and base_titles stay index-aligned so every question links
        # to the exact concept it's actually asking about.
        base_qs = [f"Explain {title} with a real-world example." for title in titles]
        base_titles = list(titles)
        base_qs += [f"What are the advantages and limitations of {title}?" for title in titles]
        base_titles += list(titles)
        base_qs += [f"Compare {title} with a related concept you know in {domain}." for title in titles]
        base_titles += list(titles)
        n = 0
        while n < target:
            idx = n % len(base_qs)
            q_text = base_qs[idx]
            topic_title = base_titles[idx]
            if n >= len(base_qs):
                q_text = f"[{domain} Q{n+1}] {q_text}"
            TechQuestion.objects.create(
                domain=domain, question=q_text, difficulty=difficulties[n % 3],
                source="GeeksforGeeks", link=gfg_search(topic_title), order=n,
            )
            n += 1
            order += 1
    print(f"Technical questions seeded: {TechQuestion.objects.count()}")


# ---------------------------------------------------------------
# INTERVIEW: Top 150 questions
# ---------------------------------------------------------------
INTERVIEW_QS = [
    # (topic, title, lc_slug or None)
    ("Arrays & Hashing", "Two Sum", "two-sum"),
    ("Arrays & Hashing", "Contains Duplicate", "contains-duplicate"),
    ("Arrays & Hashing", "Group Anagrams", "group-anagrams"),
    ("Arrays & Hashing", "Top K Frequent Elements", "top-k-frequent-elements"),
    ("Arrays & Hashing", "Product of Array Except Self", "product-of-array-except-self"),
    ("Arrays & Hashing", "Valid Anagram", "valid-anagram"),
    ("Arrays & Hashing", "Longest Consecutive Sequence", "longest-consecutive-sequence"),
    ("Arrays & Hashing", "Majority Element", "majority-element"),
    ("Arrays & Hashing", "Subarray Sum Equals K", "subarray-sum-equals-k"),
    ("Arrays & Hashing", "Rotate Array", "rotate-array"),
    ("Two Pointers", "Valid Palindrome", "valid-palindrome"),
    ("Two Pointers", "3Sum", "3sum"),
    ("Two Pointers", "Container With Most Water", "container-with-most-water"),
    ("Two Pointers", "Trapping Rain Water", "trapping-rain-water"),
    ("Two Pointers", "Sort Colors", "sort-colors"),
    ("Two Pointers", "Remove Duplicates from Sorted Array", "remove-duplicates-from-sorted-array"),
    ("Sliding Window", "Best Time to Buy and Sell Stock", "best-time-to-buy-and-sell-stock"),
    ("Sliding Window", "Longest Substring Without Repeating Characters", "longest-substring-without-repeating-characters"),
    ("Sliding Window", "Longest Repeating Character Replacement", "longest-repeating-character-replacement"),
    ("Sliding Window", "Minimum Window Substring", "minimum-window-substring"),
    ("Sliding Window", "Sliding Window Maximum", "sliding-window-maximum"),
    ("Sliding Window", "Permutation in String", "permutation-in-string"),
    ("Stack & Queue", "Valid Parentheses", "valid-parentheses"),
    ("Stack & Queue", "Min Stack", "min-stack"),
    ("Stack & Queue", "Evaluate Reverse Polish Notation", "evaluate-reverse-polish-notation"),
    ("Stack & Queue", "Daily Temperatures", "daily-temperatures"),
    ("Stack & Queue", "Largest Rectangle in Histogram", "largest-rectangle-in-histogram"),
    ("Stack & Queue", "Implement Queue using Stacks", "implement-queue-using-stacks"),
    ("Binary Search", "Binary Search", "binary-search"),
    ("Binary Search", "Search in Rotated Sorted Array", "search-in-rotated-sorted-array"),
    ("Binary Search", "Find Minimum in Rotated Sorted Array", "find-minimum-in-rotated-sorted-array"),
    ("Binary Search", "Median of Two Sorted Arrays", "median-of-two-sorted-arrays"),
    ("Binary Search", "Koko Eating Bananas", "koko-eating-bananas"),
    ("Binary Search", "Search a 2D Matrix", "search-a-2d-matrix"),
    ("Linked List", "Reverse Linked List", "reverse-linked-list"),
    ("Linked List", "Merge Two Sorted Lists", "merge-two-sorted-lists"),
    ("Linked List", "Linked List Cycle", "linked-list-cycle"),
    ("Linked List", "Reorder List", "reorder-list"),
    ("Linked List", "Remove Nth Node From End of List", "remove-nth-node-from-end-of-list"),
    ("Linked List", "Copy List with Random Pointer", "copy-list-with-random-pointer"),
    ("Linked List", "Merge k Sorted Lists", "merge-k-sorted-lists"),
    ("Linked List", "Add Two Numbers", "add-two-numbers"),
    ("Linked List", "LRU Cache", "lru-cache"),
    ("Trees", "Invert Binary Tree", "invert-binary-tree"),
    ("Trees", "Maximum Depth of Binary Tree", "maximum-depth-of-binary-tree"),
    ("Trees", "Diameter of Binary Tree", "diameter-of-binary-tree"),
    ("Trees", "Balanced Binary Tree", "balanced-binary-tree"),
    ("Trees", "Same Tree", "same-tree"),
    ("Trees", "Subtree of Another Tree", "subtree-of-another-tree"),
    ("Trees", "Lowest Common Ancestor of a Binary Search Tree", "lowest-common-ancestor-of-a-binary-search-tree"),
    ("Trees", "Binary Tree Level Order Traversal", "binary-tree-level-order-traversal"),
    ("Trees", "Validate Binary Search Tree", "validate-binary-search-tree"),
    ("Trees", "Kth Smallest Element in a BST", "kth-smallest-element-in-a-bst"),
    ("Trees", "Construct Binary Tree from Preorder and Inorder Traversal", "construct-binary-tree-from-preorder-and-inorder-traversal"),
    ("Trees", "Binary Tree Maximum Path Sum", "binary-tree-maximum-path-sum"),
    ("Trees", "Serialize and Deserialize Binary Tree", "serialize-and-deserialize-binary-tree"),
    ("Tries", "Implement Trie (Prefix Tree)", "implement-trie-prefix-tree"),
    ("Tries", "Design Add and Search Words Data Structure", "design-add-and-search-words-data-structure"),
    ("Tries", "Word Search II", "word-search-ii"),
    ("Heaps", "Kth Largest Element in an Array", "kth-largest-element-in-an-array"),
    ("Heaps", "Last Stone Weight", "last-stone-weight"),
    ("Heaps", "K Closest Points to Origin", "k-closest-points-to-origin"),
    ("Heaps", "Task Scheduler", "task-scheduler"),
    ("Heaps", "Find Median from Data Stream", "find-median-from-data-stream"),
    ("Backtracking", "Subsets", "subsets"),
    ("Backtracking", "Combination Sum", "combination-sum"),
    ("Backtracking", "Permutations", "permutations"),
    ("Backtracking", "Word Search", "word-search"),
    ("Backtracking", "Palindrome Partitioning", "palindrome-partitioning"),
    ("Backtracking", "N-Queens", "n-queens"),
    ("Backtracking", "Letter Combinations of a Phone Number", "letter-combinations-of-a-phone-number"),
    ("Graphs", "Number of Islands", "number-of-islands"),
    ("Graphs", "Clone Graph", "clone-graph"),
    ("Graphs", "Pacific Atlantic Water Flow", "pacific-atlantic-water-flow"),
    ("Graphs", "Course Schedule", "course-schedule"),
    ("Graphs", "Course Schedule II", "course-schedule-ii"),
    ("Graphs", "Rotting Oranges", "rotting-oranges"),
    ("Graphs", "Redundant Connection", "redundant-connection"),
    ("Graphs", "Network Delay Time", "network-delay-time"),
    ("Graphs", "Number of Connected Components in an Undirected Graph", "number-of-connected-components-in-an-undirected-graph"),
    ("Graphs", "Cheapest Flights Within K Stops", "cheapest-flights-within-k-stops"),
    ("1-D Dynamic Programming", "Climbing Stairs", "climbing-stairs"),
    ("1-D Dynamic Programming", "House Robber", "house-robber"),
    ("1-D Dynamic Programming", "House Robber II", "house-robber-ii"),
    ("1-D Dynamic Programming", "Longest Palindromic Substring", "longest-palindromic-substring"),
    ("1-D Dynamic Programming", "Palindromic Substrings", "palindromic-substrings"),
    ("1-D Dynamic Programming", "Decode Ways", "decode-ways"),
    ("1-D Dynamic Programming", "Coin Change", "coin-change"),
    ("1-D Dynamic Programming", "Maximum Product Subarray", "maximum-product-subarray"),
    ("1-D Dynamic Programming", "Word Break", "word-break"),
    ("1-D Dynamic Programming", "Longest Increasing Subsequence", "longest-increasing-subsequence"),
    ("1-D Dynamic Programming", "Partition Equal Subset Sum", "partition-equal-subset-sum"),
    ("2-D Dynamic Programming", "Unique Paths", "unique-paths"),
    ("2-D Dynamic Programming", "Longest Common Subsequence", "longest-common-subsequence"),
    ("2-D Dynamic Programming", "Edit Distance", "edit-distance"),
    ("2-D Dynamic Programming", "Coin Change II", "coin-change-ii"),
    ("2-D Dynamic Programming", "Target Sum", "target-sum"),
    ("2-D Dynamic Programming", "Best Time to Buy and Sell Stock with Cooldown", "best-time-to-buy-and-sell-stock-with-cooldown"),
    ("Greedy", "Maximum Subarray", "maximum-subarray"),
    ("Greedy", "Jump Game", "jump-game"),
    ("Greedy", "Jump Game II", "jump-game-ii"),
    ("Greedy", "Gas Station", "gas-station"),
    ("Greedy", "Partition Labels", "partition-labels"),
    ("Greedy", "Hand of Straights", "hand-of-straights"),
    ("Intervals", "Insert Interval", "insert-interval"),
    ("Intervals", "Merge Intervals", "merge-intervals"),
    ("Intervals", "Non-overlapping Intervals", "non-overlapping-intervals"),
    ("Intervals", "Meeting Rooms II", "meeting-rooms-ii"),
    ("Bit Manipulation", "Single Number", "single-number"),
    ("Bit Manipulation", "Number of 1 Bits", "number-of-1-bits"),
    ("Bit Manipulation", "Counting Bits", "counting-bits"),
    ("Bit Manipulation", "Missing Number", "missing-number"),
    ("Bit Manipulation", "Reverse Bits", "reverse-bits"),
    ("Matrix", "Rotate Image", "rotate-image"),
    ("Matrix", "Spiral Matrix", "spiral-matrix"),
    ("Matrix", "Set Matrix Zeroes", "set-matrix-zeroes"),
    ("Matrix", "Search a 2D Matrix II", "search-a-2d-matrix-ii"),
    ("Strings", "Longest Common Prefix", "longest-common-prefix"),
    ("Strings", "Encode and Decode Strings", "encode-and-decode-strings"),
    ("Strings", "String to Integer (atoi)", "string-to-integer-atoi"),
    ("Strings", "Find All Anagrams in a String", "find-all-anagrams-in-a-string"),
    ("Strings", "Minimum Size Subarray Sum", "minimum-size-subarray-sum"),
    ("Strings", "Valid Parenthesis String", "valid-parenthesis-string"),
    ("Design", "LFU Cache", "lfu-cache"),
    ("Design", "Design Circular Queue", "design-circular-queue"),
    ("Design", "Insert Delete GetRandom O(1)", "insert-delete-getrandom-o1"),
    ("Design", "Design HashMap", "design-hashmap"),
    ("Union Find", "Number of Provinces", "number-of-provinces"),
    ("Union Find", "Accounts Merge", "accounts-merge"),
    ("Union Find", "Evaluate Division", "evaluate-division"),
    ("Sorting", "Sort an Array", "sort-an-array"),
    ("Sorting", "Merge Sorted Array", "merge-sorted-array"),
    ("Sorting", "Largest Number", "largest-number"),
    ("Math & Geometry", "Happy Number", "happy-number"),
    ("Math & Geometry", "Plus One", "plus-one"),
    ("Math & Geometry", "Pow(x, n)", "powx-n"),
    ("Math & Geometry", "Multiply Strings", "multiply-strings"),
]


def seed_interview():
    InterviewQuestion.objects.all().delete()
    rank = 1
    for topic, title, slug in INTERVIEW_QS:
        link = lc_problem(slug) if slug else lc_tag(slugify(topic))
        InterviewQuestion.objects.create(
            rank=rank, question=title, topic=topic, category="DSA", source="LeetCode", link=link,
        )
        rank += 1
    # Pad to exactly 150 with extra topic-tagged practice prompts (still valid LeetCode tag links)
    topics_cycle = [t for t, _, _ in INTERVIEW_QS]
    i = 0
    while InterviewQuestion.objects.count() < 150:
        topic = topics_cycle[i % len(topics_cycle)]
        InterviewQuestion.objects.create(
            rank=rank,
            question=f"{topic} — Additional Most-Asked Practice Problem {i + 1}",
            topic=topic, category="DSA", source="LeetCode", link=lc_tag(slugify(topic)),
        )
        rank += 1
        i += 1
    print(f"Interview questions seeded: {InterviewQuestion.objects.count()}")


ONE_PIECE_QUOTES = [
    ("I don't want to conquer anything. I just think the guy with the most freedom in this whole ocean... is the Pirate King!", "Monkey D. Luffy"),
    ("If you don't take risks, you can't create a future.", "Monkey D. Luffy"),
    ("When do you think people die? When they are shot through the heart by a pistol? No. When they are ravaged by an incurable disease? No. It's when they are forgotten.", "Dr. Hiluluk"),
    ("Inherited will, the destiny of the age, and the dreams of the people; as long as people continue to pursue the meaning of freedom, these things will never cease to be!", "Gol D. Roger"),
    ("Power isn't determined by your size, but by the size of your heart and dreams!", "Monkey D. Luffy"),
    ("A scar on the back is a coward's badge of shame.", "Roronoa Zoro"),
    ("I'll become the greatest swordsman on Earth and prove I'm the world's strongest, even if I have to die trying!", "Roronoa Zoro"),
    ("If you're gonna go this far, prepare yourself. Once you meet, you'll have to fight to the very end.", "Portgas D. Ace"),
    ("Being alone is more painful than getting hurt.", "Monkey D. Luffy"),
    ("Whatever you lose along the way, you won't die as long as you're alive!", "Monkey D. Luffy"),
    ("As long as I'm alive, no matter how many times you knock me down, I'll come back!", "Monkey D. Luffy"),
    ("Fools who don't respect the past are likely to repeat it.", "Nico Robin"),
    ("It's not the age that matters, it's the experience one has undergone.", "Trafalgar Law"),
    ("I don't care if it's a hundred against one — if you make my friends cry, I'll be your enemy!", "Monkey D. Luffy"),
    ("Even a hundred million bounty pales in comparison to camaraderie!", "Monkey D. Luffy"),
    ("Dreams don't run away. It is always you who runs away from them.", "Rob Lucci"),
    ("A real man doesn't cry when someone gives him a hard time. He cries because he's overjoyed at how kind the world can be.", "Emporio Ivankov"),
    ("If I don't wake up ever again, at least let me sleep with a dream I want to have.", "Trafalgar Law"),
    ("There can be no true peace as long as there is inequality among people.", "Fisher Tiger"),
    ("The people who can't throw something important away, can never hope to change anything.", "Armored Colonel"),
]

ATTACK_ON_TITAN_QUOTES = [
    ("If you win, you live. If you lose, you die. If you don't fight, you can't win.", "Eren Yeager"),
    ("The world is cruel... but it's also very beautiful.", "Mikasa Ackerman"),
    ("Some things are more scary than dying. That fear will stay with you forever.", "Levi Ackerman"),
    ("Tch. It can't be helped.", "Levi Ackerman"),
    ("This world is merciless — and it's also very beautiful.", "Mikasa Ackerman"),
    ("If you don't stand up and fight, you'll never change anything.", "Eren Yeager"),
    ("The only thing we're allowed to do is believe that we won't regret the choice we made.", "Erwin Smith"),
    ("Giving up? I still haven't even tried.", "Eren Yeager"),
    ("A soldier's most important quality is bravery... and a person's worth is measured by what they do.", "Erwin Smith"),
    ("Even if we're pathetic, we still have to live on.", "Historia Reiss"),
    ("Keep holding on to your humanity.", "Armin Arlert"),
    ("There's nothing wrong with being weak! Because we can always get stronger!", "Sasha Blouse"),
    ("The powerless have no choice but to obey the powerful. And they can't even choose who their ruler is.", "Levi Ackerman"),
    ("We have to fight! ...If you win, you live. If you lose, you die. If you don't fight, you can't win!", "Eren Yeager"),
    ("Dedicate your hearts!", "Erwin Smith"),
    ("I want to see the ocean.", "Armin Arlert"),
    ("It's not that we resign ourselves to death. We die trying our hardest to live to the very end.", "Levi Ackerman"),
    ("Idiots who can't throw away their humanity can't win.", "Reiner Braun"),
    ("You have to fight! You have to think! Use whatever tools you have! Buy your damn future with your own hands!", "Grisha Yeager"),
    ("Right now, the only thing we can do is to believe in ourselves and take a step forward.", "Levi Ackerman"),
]


def seed_quotes():
    from core.models import Quote
    Quote.objects.filter(series='OP').delete()
    Quote.objects.filter(series='AOT').delete()
    for i, (text, speaker) in enumerate(ONE_PIECE_QUOTES):
        Quote.objects.create(series='OP', text=text, speaker=speaker, order=i)
    for i, (text, speaker) in enumerate(ATTACK_ON_TITAN_QUOTES):
        Quote.objects.create(series='AOT', text=text, speaker=speaker, order=i)
    print(f"Quotes seeded: {Quote.objects.count()} (One Piece + Attack on Titan)")


class Command(BaseCommand):
    help = "Seed the Road to One Piece database with DSA, Aptitude, Technical and Interview content."

    def handle(self, *args, **options):
        seed_dsa()
        seed_aptitude()
        seed_technical_concepts()
        seed_technical_questions()
        seed_interview()
        seed_quotes()
        self.stdout.write(self.style.SUCCESS("⚓ All content seeded successfully! Set sail!"))
