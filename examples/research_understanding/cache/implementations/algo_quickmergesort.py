# QuickMergeSort
#
# Purpose: QuickMergeSort aims to combine the strengths of QuickSort and MergeSort, achieving good average-case performance while maintaining good worst-case bounds.

def quickmergesort(arr, low = 0, high = None):
    """
    QuickMergeSort

    QuickMergeSort aims to combine the strengths of QuickSort and MergeSort, achieving good average-case performance while maintaining good worst-case bounds.

    Args:
        arr: The array to be sorted
        low: The starting index of the array segment to sort
        high: The ending index of the array segment to sort

    Returns:
        Sorted array
    """
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

    return arr


def insertion_sort(arr, low, high):
    for i in range(low + 1, high + 1):
        key = arr[i]
        j = i - 1
        while j >= low and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def is_merging_beneficial(arr, low, pivot, high):
    # In a real implementation, this would use heuristics
    # For this example, we'll merge if the segments are imbalanced
    left_size = pivot - low + 1
    right_size = high - pivot
    return abs(left_size - right_size) > (high - low) // 4


def merge(arr, low, pivot, high):
    # Create temporary arrays for the left and right segments
    left_size = pivot - low + 1
    right_size = high - pivot
    left = [arr[low + i] for i in range(left_size)]
    right = [arr[pivot + 1 + i] for i in range(right_size)]
    
    # Merge the arrays back into arr[low..high]
    i, j, k = 0, 0, low
    
    while i < left_size and j < right_size:
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1
    
    # Copy any remaining elements
    while i < left_size:
        arr[k] = left[i]
        i += 1
        k += 1
    
    while j < right_size:
        arr[k] = right[j]
        j += 1
        k += 1
    
    return arr