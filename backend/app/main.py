"""
main.py — FastAPI application entry point.

On startup:
  1. Creates all DB tables
  2. Seeds sample problems if the DB is empty
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from app.database import engine, AsyncSessionLocal, Base
from app.models import Problem
from app.routes import auth, problems, submissions

app = FastAPI(title="CodeLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(problems.router)
app.include_router(submissions.router)


SEED_PROBLEMS = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "description": (
            "Given a list of integers `nums` and a target integer `target`, "
            "return the indices of the two numbers that add up to the target.\n\n"
            "You may assume each input has exactly one solution, and you may not use the same element twice.\n\n"
            "**Example:**\n```\nnums = [2, 7, 11, 15], target = 9\nOutput: [0, 1]\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(nums: list[int], target: int) -> list[int]:\n    # your code here\n    pass\n",
        "solution_hint": "Use a hash map to store each number and its index. For each number, check if target-number is already in the map.",
        "test_cases": [
            {"input": "[2, 7, 11, 15], 9", "expected": "[0, 1]", "is_hidden": False},
            {"input": "[3, 2, 4], 6", "expected": "[1, 2]", "is_hidden": False},
            {"input": "[3, 3], 6", "expected": "[0, 1]", "is_hidden": False},
            {"input": "[], 0", "expected": "[]", "is_hidden": True},
            {"input": "[1, 2, 3, 4, 5], 9", "expected": "[3, 4]", "is_hidden": True},
        ],
    },
    {
        "title": "Valid Palindrome",
        "slug": "valid-palindrome",
        "description": (
            "A phrase is a palindrome if, after converting all uppercase letters to lowercase "
            "and removing all non-alphanumeric characters, it reads the same forward and backward.\n\n"
            "Given a string `s`, return `True` if it is a palindrome, or `False` otherwise.\n\n"
            "**Example:**\n```\ns = 'A man, a plan, a canal: Panama'\nOutput: True\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(s: str) -> bool:\n    # your code here\n    pass\n",
        "solution_hint": "Clean the string to only alphanumeric lowercase chars, then compare it to its reverse.",
        "test_cases": [
            {"input": "'A man, a plan, a canal: Panama'", "expected": "True", "is_hidden": False},
            {"input": "'race a car'", "expected": "False", "is_hidden": False},
            {"input": "' '", "expected": "True", "is_hidden": False},
            {"input": "''", "expected": "True", "is_hidden": True},
            {"input": "'No lemon, no melon'", "expected": "True", "is_hidden": True},
        ],
    },
    {
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "description": (
            "Given an integer array `nums`, find the subarray with the largest sum and return its sum.\n\n"
            "**Example:**\n```\nnums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]\nOutput: 6\n# Subarray [4, -1, 2, 1] has the largest sum\n```"
        ),
        "difficulty": "medium",
        "starter_code": "def solution(nums: list[int]) -> int:\n    # your code here\n    pass\n",
        "solution_hint": "Kadane's algorithm: keep a running sum, reset to 0 when it goes negative, track the maximum seen.",
        "test_cases": [
            {"input": "[-2, 1, -3, 4, -1, 2, 1, -5, 4]", "expected": "6", "is_hidden": False},
            {"input": "[1]", "expected": "1", "is_hidden": False},
            {"input": "[5, 4, -1, 7, 8]", "expected": "23", "is_hidden": False},
            {"input": "[-1, -2, -3]", "expected": "-1", "is_hidden": True},
            {"input": "[0, 0, 0]", "expected": "0", "is_hidden": True},
        ],
    },
    {
        "title": "Climbing Stairs",
        "slug": "climbing-stairs",
        "description": (
            "You are climbing a staircase. It takes `n` steps to reach the top. "
            "Each time you can climb 1 or 2 steps. "
            "Return the number of distinct ways you can climb to the top.\n\n"
            "**Example:**\n```\nn = 3\nOutput: 3\n# Ways: [1,1,1], [1,2], [2,1]\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(n: int) -> int:\n    # your code here\n    pass\n",
        "solution_hint": "This is a Fibonacci-style problem. ways(n) = ways(n-1) + ways(n-2).",
        "test_cases": [
            {"input": "2", "expected": "2", "is_hidden": False},
            {"input": "3", "expected": "3", "is_hidden": False},
            {"input": "5", "expected": "8", "is_hidden": False},
            {"input": "1", "expected": "1", "is_hidden": True},
            {"input": "10", "expected": "89", "is_hidden": True},
        ],
    },
    {
        "title": "Longest Common Prefix",
        "slug": "longest-common-prefix",
        "description": (
            "Write a function to find the longest common prefix string among a list of strings.\n"
            "If there is no common prefix, return an empty string `''`.\n\n"
            "**Example:**\n```\nstrs = ['flower', 'flow', 'flight']\nOutput: 'fl'\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(strs: list[str]) -> str:\n    # your code here\n    pass\n",
        "solution_hint": "Sort the list. The common prefix of all strings is the common prefix of the first and last strings.",
        "test_cases": [
            {"input": "['flower', 'flow', 'flight']", "expected": "'fl'", "is_hidden": False},
            {"input": "['dog', 'racecar', 'car']", "expected": "''", "is_hidden": False},
            {"input": "['interview', 'inter', 'internal']", "expected": "'inter'", "is_hidden": False},
            {"input": "[]", "expected": "''", "is_hidden": True},
            {"input": "['a']", "expected": "'a'", "is_hidden": True},
        ],
    },
    {
        "title": "Contains Duplicate",
        "slug": "contains-duplicate",
        "description": (
            "Given an integer array `nums`, return `True` if any value appears "
            "at least twice in the array, and return `False` if every element is distinct.\n\n"
            "**Example:**\n```\nnums = [1, 2, 3, 1]\nOutput: True\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(nums: list[int]) -> bool:\n    # your code here\n    pass\n",
        "solution_hint": "Use a set. If a number is already in the set, return True. Otherwise add it.",
        "test_cases": [
            {"input": "[1, 2, 3, 1]", "expected": "True", "is_hidden": False},
            {"input": "[1, 2, 3, 4]", "expected": "False", "is_hidden": False},
            {"input": "[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]", "expected": "True", "is_hidden": False},
            {"input": "[]", "expected": "False", "is_hidden": True},
            {"input": "[7]", "expected": "False", "is_hidden": True},
        ],
    },
    {
        "title": "Valid Anagram",
        "slug": "valid-anagram",
        "description": (
            "Given two strings `s` and `t`, return `True` if `t` is an anagram of `s`, "
            "and `False` otherwise.\n\n"
            "**Example:**\n```\ns = 'anagram', t = 'nagaram'\nOutput: True\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(s: str, t: str) -> bool:\n    # your code here\n    pass\n",
        "solution_hint": "Sort both strings and compare, or count character frequencies with a dictionary.",
        "test_cases": [
            {"input": "'anagram', 'nagaram'", "expected": "True", "is_hidden": False},
            {"input": "'rat', 'car'", "expected": "False", "is_hidden": False},
            {"input": "'a', 'a'", "expected": "True", "is_hidden": False},
            {"input": "'', ''", "expected": "True", "is_hidden": True},
            {"input": "'a', 'ab'", "expected": "False", "is_hidden": True},
        ],
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "slug": "best-time-to-buy-and-sell-stock",
        "description": (
            "Given an array `prices` where `prices[i]` is the price of a stock on day `i`, "
            "find the maximum profit from buying on one day and selling on a later day. "
            "If no profit is possible, return `0`.\n\n"
            "**Example:**\n```\nprices = [7, 1, 5, 3, 6, 4]\nOutput: 5\n# Buy on day 2 (price=1), sell on day 5 (price=6)\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(prices: list[int]) -> int:\n    # your code here\n    pass\n",
        "solution_hint": "Track the minimum price seen so far, and the best profit (current price - min so far) at each step.",
        "test_cases": [
            {"input": "[7, 1, 5, 3, 6, 4]", "expected": "5", "is_hidden": False},
            {"input": "[7, 6, 4, 3, 1]", "expected": "0", "is_hidden": False},
            {"input": "[1, 2]", "expected": "1", "is_hidden": False},
            {"input": "[2, 4, 1]", "expected": "2", "is_hidden": True},
            {"input": "[3, 3, 3]", "expected": "0", "is_hidden": True},
        ],
    },
    {
        "title": "Single Number",
        "slug": "single-number",
        "description": (
            "Given a non-empty array of integers `nums`, every element appears twice except for one. "
            "Find that single element.\n\n"
            "**Example:**\n```\nnums = [4, 1, 2, 1, 2]\nOutput: 4\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(nums: list[int]) -> int:\n    # your code here\n    pass\n",
        "solution_hint": "XOR every number together. Pairs cancel out (a ^ a = 0), leaving only the single number.",
        "test_cases": [
            {"input": "[2, 2, 1]", "expected": "1", "is_hidden": False},
            {"input": "[4, 1, 2, 1, 2]", "expected": "4", "is_hidden": False},
            {"input": "[1]", "expected": "1", "is_hidden": False},
            {"input": "[0, 1, 0]", "expected": "1", "is_hidden": True},
            {"input": "[5, 3, 5]", "expected": "3", "is_hidden": True},
        ],
    },
    {
        "title": "Missing Number",
        "slug": "missing-number",
        "description": (
            "Given an array `nums` containing `n` distinct numbers in the range `[0, n]`, "
            "return the one number in the range that is missing.\n\n"
            "**Example:**\n```\nnums = [3, 0, 1]\nOutput: 2\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(nums: list[int]) -> int:\n    # your code here\n    pass\n",
        "solution_hint": "The sum of 0..n is n*(n+1)/2. Subtract the actual sum of nums from this to get the missing number.",
        "test_cases": [
            {"input": "[3, 0, 1]", "expected": "2", "is_hidden": False},
            {"input": "[0, 1]", "expected": "2", "is_hidden": False},
            {"input": "[9, 6, 4, 2, 3, 5, 7, 0, 1]", "expected": "8", "is_hidden": False},
            {"input": "[0]", "expected": "1", "is_hidden": True},
            {"input": "[1]", "expected": "0", "is_hidden": True},
        ],
    },
    {
        "title": "Majority Element",
        "slug": "majority-element",
        "description": (
            "Given an array `nums` of size `n`, return the majority element — "
            "the element that appears more than `n // 2` times. "
            "You may assume the majority element always exists.\n\n"
            "**Example:**\n```\nnums = [2, 2, 1, 1, 1, 2, 2]\nOutput: 2\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(nums: list[int]) -> int:\n    # your code here\n    pass\n",
        "solution_hint": "Boyer-Moore voting algorithm: track a candidate and a count, adjusting as you scan. Or just use a dictionary to count frequencies.",
        "test_cases": [
            {"input": "[3, 2, 3]", "expected": "3", "is_hidden": False},
            {"input": "[2, 2, 1, 1, 1, 2, 2]", "expected": "2", "is_hidden": False},
            {"input": "[1]", "expected": "1", "is_hidden": False},
            {"input": "[6, 5, 5]", "expected": "5", "is_hidden": True},
            {"input": "[1, 1, 1, 2, 2]", "expected": "1", "is_hidden": True},
        ],
    },
    {
        "title": "Reverse Integer",
        "slug": "reverse-integer",
        "description": (
            "Given a signed 32-bit integer `x`, return `x` with its digits reversed. "
            "The sign should be preserved.\n\n"
            "**Example:**\n```\nx = 123\nOutput: 321\n\nx = -123\nOutput: -321\n```"
        ),
        "difficulty": "medium",
        "starter_code": "def solution(x: int) -> int:\n    # your code here\n    pass\n",
        "solution_hint": "Take the absolute value, repeatedly extract the last digit with %10 and build the reversed number, then reapply the sign at the end.",
        "test_cases": [
            {"input": "123", "expected": "321", "is_hidden": False},
            {"input": "-123", "expected": "-321", "is_hidden": False},
            {"input": "120", "expected": "21", "is_hidden": False},
            {"input": "0", "expected": "0", "is_hidden": True},
            {"input": "100", "expected": "1", "is_hidden": True},
        ],
    },
    {
        "title": "Binary Search",
        "slug": "binary-search",
        "description": (
            "Given a sorted array of integers `nums` and an integer `target`, "
            "return the index of `target` if it exists, or `-1` if it does not.\n\n"
            "**Example:**\n```\nnums = [-1, 0, 3, 5, 9, 12], target = 9\nOutput: 4\n```"
        ),
        "difficulty": "easy",
        "starter_code": "def solution(nums: list[int], target: int) -> int:\n    # your code here\n    pass\n",
        "solution_hint": "Keep low and high pointers, compute mid, and narrow the search range based on whether nums[mid] is less than, greater than, or equal to target.",
        "test_cases": [
            {"input": "[-1, 0, 3, 5, 9, 12], 9", "expected": "4", "is_hidden": False},
            {"input": "[-1, 0, 3, 5, 9, 12], 2", "expected": "-1", "is_hidden": False},
            {"input": "[5], 5", "expected": "0", "is_hidden": False},
            {"input": "[], 5", "expected": "-1", "is_hidden": True},
            {"input": "[1, 2, 3, 4, 5], 1", "expected": "0", "is_hidden": True},
        ],
    },
    {
        "title": "Product of Array Except Self",
        "slug": "product-of-array-except-self",
        "description": (
            "Given an integer array `nums`, return an array `answer` such that `answer[i]` "
            "is equal to the product of all elements of `nums` except `nums[i]`. "
            "Do not use the division operator.\n\n"
            "**Example:**\n```\nnums = [1, 2, 3, 4]\nOutput: [24, 12, 8, 6]\n```"
        ),
        "difficulty": "medium",
        "starter_code": "def solution(nums: list[int]) -> list[int]:\n    # your code here\n    pass\n",
        "solution_hint": "Build a prefix-products array and a suffix-products array, then multiply them element-wise. This avoids division entirely.",
        "test_cases": [
            {"input": "[1, 2, 3, 4]", "expected": "[24, 12, 8, 6]", "is_hidden": False},
            {"input": "[-1, 1, 0, -3, 3]", "expected": "[0, 0, 9, 0, 0]", "is_hidden": False},
            {"input": "[2, 3]", "expected": "[3, 2]", "is_hidden": False},
            {"input": "[1, 1, 1]", "expected": "[1, 1, 1]", "is_hidden": True},
            {"input": "[5]", "expected": "[1]", "is_hidden": True},
        ],
    },
    {
        "title": "Merge Intervals",
        "slug": "merge-intervals",
        "description": (
            "Given an array of intervals where `intervals[i] = [start, end]`, merge all "
            "overlapping intervals and return an array of the non-overlapping intervals "
            "that cover all the input intervals, sorted by start.\n\n"
            "**Example:**\n```\nintervals = [[1,3],[2,6],[8,10],[15,18]]\nOutput: [[1,6],[8,10],[15,18]]\n```"
        ),
        "difficulty": "medium",
        "starter_code": "def solution(intervals: list[list[int]]) -> list[list[int]]:\n    # your code here\n    pass\n",
        "solution_hint": "Sort intervals by start time. Then walk through them, merging the current interval into the last one if they overlap, otherwise appending it as a new interval.",
        "test_cases": [
            {"input": "[[1, 3], [2, 6], [8, 10], [15, 18]]", "expected": "[[1, 6], [8, 10], [15, 18]]", "is_hidden": False},
            {"input": "[[1, 4], [4, 5]]", "expected": "[[1, 5]]", "is_hidden": False},
            {"input": "[[1, 4]]", "expected": "[[1, 4]]", "is_hidden": False},
            {"input": "[[1, 4], [0, 4]]", "expected": "[[0, 4]]", "is_hidden": True},
            {"input": "[[1, 4], [2, 3]]", "expected": "[[1, 4]]", "is_hidden": True},
        ],
    },
]


async def seed_problems(db):
    result = await db.execute(select(Problem).limit(1))
    if result.scalar_one_or_none():
        return  # already seeded

    for p in SEED_PROBLEMS:
        problem = Problem(**p)
        db.add(problem)
    await db.commit()
    print(f"✅ Seeded {len(SEED_PROBLEMS)} problems")


@app.on_event("startup")
async def startup():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables ready")

    # Seed problems
    async with AsyncSessionLocal() as db:
        await seed_problems(db)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "CodeLens API"}
