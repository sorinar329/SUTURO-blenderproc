from enum import Enum, auto
import numpy as np
import blenderproc as bproc


class PartitionType(Enum):
    EQUAL_OBJECTS = auto()  # Gleichartige Objekte in der Partition
    UNIQUE_OBJECTS = auto()  # Partitionen, in denen dieselben Objekte nie auftauchen können
    LESS_PROBABLE_OBJECTS = auto()


def validate_partitions(partition) -> None:
    assert isinstance(partition, list)
    for mesh_object in partition:
        try:
            mesh_object.get_name()
        except ReferenceError:
            partition.remove(mesh_object)

    assert len(partition) > 0


class ObjectPartition:
    def __init__(self, num_partitions: int, objects: [bproc.types.MeshObject]):
        if num_partitions <= 1:
            raise AssertionError("The minimum amount of partitions should be at least 2")

        self.num_partitions = num_partitions
        self.objects = objects
        self._partitions = None

        if len(self.objects) - len(self.objects) % self.num_partitions == 0:
            raise ValueError("Partitions size is set to high in comparison to objects list lenght")

    def create_partition(self, partition_type: PartitionType,
                         probability_reduction_factor: float = 0.99) -> [[bproc.types.MeshObject]]:
        objects = np.asarray(self.objects)
        np.random.shuffle(objects)
        # Ensure that partitions created evenly
        objects = objects[0:(len(self.objects) - len(self.objects) % self.num_partitions)]
        num_objects = objects.shape[0]

        partitions = np.split(objects, self.num_partitions)
        if partition_type == PartitionType.EQUAL_OBJECTS:
            self._partitions = partitions
            return partitions

        # Deletes duplicate objects, maybe rework it later
        if partition_type == PartitionType.UNIQUE_OBJECTS:
            object_names = [[o.get_name().split('.')[0] for o in partition] for partition in partitions]
            for i, row in enumerate(object_names):
                row = np.array(row)
                indices = np.argsort(row)
                _, count = np.unique(row, return_counts=True)
                objects_sorted = np.take_along_axis(partitions[i], indices, axis=-1)
                for j, c in enumerate(count):
                    if c > 1:
                        partitions[i] = np.delete(objects_sorted, np.s_[j + 1:j + c])

            self._partitions = partitions
            return partitions

        if partition_type == PartitionType.LESS_PROBABLE_OBJECTS:
            if not (0 < probability_reduction_factor < 1):
                raise Exception("Probabilities either become negative or you increase the likelihood"
                                "of the same object being drawn ")
            object_names = np.asarray([o.get_name().split('.')[0] for o in objects])
            partitions_size = int(num_objects / self.num_partitions)
            partitions = np.empty(shape=[self.num_partitions, partitions_size], dtype=object)
            for i in range(self.num_partitions):
                probabilities = np.repeat(a=1 / num_objects, repeats=num_objects)
                for j in range(partitions_size):
                    selected_idx = np.random.choice(np.arange(num_objects), size=1, p=probabilities)[0]
                    selected_object = objects[selected_idx]
                    # Aktualisieren der Partition und Objektlisten
                    partitions[i, j] = selected_object
                    object_indices = (object_names == object_names[selected_idx])
                    probabilities[object_indices] *= probability_reduction_factor
                    # Entfernen des ausgewählten Objekts
                    object_names = np.delete(object_names, selected_idx)
                    probabilities = np.delete(probabilities, selected_idx)
                    objects = np.delete(objects, selected_idx)

                    # Normalisieren der Wahrscheinlichkeiten
                    probabilities /= np.sum(probabilities)
                    num_objects -= 1
            self._partitions = partitions
            return partitions.tolist()

    # Return previously created partition
    def get_partition(self):
        return self._partitions
