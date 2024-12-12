class Solution:
    def findDuplicate(self, nums):
        # Phase 1: Find the intersection point of the two runners
        slow = nums[0]
        fast = nums[0]

        # Step 1: Move slow by 1 step, fast by 2 steps until they meet
        while True:
            slow = nums[slow]
            fast = nums[nums[fast]]
            if slow == fast:
                break

        # Phase 2: Find the entry point to the cycle
        slow = nums[0]
        while slow != fast:
            slow = nums[slow]
            fast = nums[fast]

        return slow
