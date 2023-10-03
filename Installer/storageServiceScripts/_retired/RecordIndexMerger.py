class RecordIndexMerger:
    @staticmethod
    def mergeIndexes(left, right):
        global debug
        debug.log("Merging RIGHT index INTO LEFT index...")
        if left is None:
            left = right
        elif right is None:
            sortedDict = left
        elif not right:
            sortedDict = left
        else:
            try:
                for key, value in right.items():
                    # debug.log(key, value)
                    # isInLeft = key in left
                    # debug.log(isInLeft)
                    if key in left:
                        for item in value:
                            if item not in left[key]:
                                left[key].append(item)
                    else:
                        left[key] = []
                        for item in value:
                            left[key].append(item)
            except Exception as e:
                debug.log(f"mergeIndexes failure!\n{e}", forceLog=True)

            sortedDict = dict(sorted(left.items()))

        return sortedDict
