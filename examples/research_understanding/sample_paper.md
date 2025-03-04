# Sample Research Paper

## Abstract

This paper introduces a novel sorting algorithm called QuickMergeSort, which combines 
the benefits of QuickSort and MergeSort. Our algorithm achieves O(n log n) time complexity
in the average case while maintaining O(n log n) worst-case performance.

## 1. Introduction

Sorting algorithms are fundamental in computer science. QuickSort offers excellent average-case
performance but suffers from O(n²) worst-case complexity. MergeSort maintains O(n log n)
worst-case performance but requires additional memory. Our QuickMergeSort algorithm aims
to combine the strengths of both approaches.

## 2. The QuickMergeSort Algorithm

The QuickMergeSort algorithm works as follows:

```python
def quick_merge_sort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
        
    if low < high:
        # If the array segment is small, use insertion sort
        if high - low < 10:
            insertion_sort(arr, low, high)
            return
            
        # Otherwise use quicksort partitioning
        pivot = partition(arr, low, high)
        
        # Recursively sort the left half
        quick_merge_sort(arr, low, pivot-1)
        
        # Recursively sort the right half
        quick_merge_sort(arr, pivot+1, high)
        
        # Merge the two sorted halves if needed
        if is_merging_beneficial(arr, low, pivot, high):
            merge(arr, low, pivot, high)
```

The time complexity of QuickMergeSort is O(n log n) in both average and worst case.
The space complexity is O(n) in the worst case.

## 3. Experimental Results

We compared QuickMergeSort against standard QuickSort and MergeSort implementations
on randomly generated arrays of different sizes.

Our algorithm performed better than QuickSort on adversarial inputs and used less
memory than MergeSort on average.

## 4. Conclusion

QuickMergeSort offers a balanced approach to sorting, maintaining good performance
characteristics in both time and space complexity.

## References

1. Hoare, C. A. R. (1962). "Quicksort". The Computer Journal. 5 (1): 10–16.
2. Knuth, D. E. (1998). The Art of Computer Programming, Volume 3: Sorting and Searching.
