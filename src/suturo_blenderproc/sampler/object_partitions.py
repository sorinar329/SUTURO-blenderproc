from enum import Enum, auto
import numpy as np
import blenderproc as bproc
import suturo_blenderproc.types.entity


class PartitionType(Enum):
    EQUAL_OBJECTS = auto()  # Gleichartige Objekte in der Partition
    UNIQUE_OBJECTS = auto()  # Partitionen, in denen dieselben Objekte nie auftauchen können
    LESS_PROBABLE_OBJECTS = auto()


class ObjectPartition(object):
    def __init__(self, num_partitions: int, objects: [bproc.types.MeshObject], partition_type: PartitionType):
        self.num_partitions = num_partitions
        self.objects = objects
        self._partitions = None
        self.partition_type = partition_type

    def create_partition(self):
        num_objects = len(self.objects)
        objects = np.asarray(self.objects)
        np.random.shuffle(objects)
        # Ensure that partitions created evenly
        objects = objects[0:(num_objects - num_objects % self.num_partitions)]
        partitions = np.split(objects, self.num_partitions)
        if self.partition_type == PartitionType.EQUAL_OBJECTS:
            self._partitions = partitions
            return partitions
        # Delete duplicate objects, maybe rework it later
        if self.partition_type == PartitionType.UNIQUE_OBJECTS:
            object_names = [[o.get_name().split('.')[0] for o in partition] for partition in partitions]
            for i, row in enumerate(object_names):
                row = np.array(row)
                indices = np.argsort(np.asarray(row))
                _, count = np.unique(row, axis=0, return_counts=True)
                objects_sorted = np.take_along_axis(partitions[i], indices, axis=-1)
                row = np.take_along_axis(row, indices, axis=-1)
                np.zeros(row.shape[0])
                for j, c in enumerate(count):
                    if c > 1:
                        partitions[i] = np.delete(objects_sorted, np.s_[j + 1:j + c])

                self._partitions = partitions
            print(partitions)
            return partitions
