import numpy as np

class DLT3D:
    def __init__(self):
        self.P = None

    def compute_dlt(self, world_points, image_points):
        """Computes the DLT using given world points and image points."""
        assert len(world_points) == len(image_points), "Number of world and image points should be the same."

        num_points = len(world_points)
        A = []

        for i in range(num_points):
            X, Y, Z = world_points[i]
            x, y = image_points[i]
            A.append([-X, -Y, -Z, -1, 0, 0, 0, 0, x*X, x*Y, x*Z, x])
            A.append([0, 0, 0, 0, -X, -Y, -Z, -1, y*X, y*Y, y*Z, y])

        A = np.array(A)
        _, _, V = np.linalg.svd(A)
        self.P = V[-1].reshape(3, 4)

    def world_to_image(self, world_point):
        """Transforms a world point to an image point using the computed P matrix."""
        assert self.P is not None, "Compute DLT before using transformations."

        world_point = np.append(world_point, 1)  # Convert to homogeneous coordinates
        image_point = np.dot(self.P, world_point)
        # Convert back to non-homogeneous coordinates
        image_point = image_point / image_point[2]
        return image_point[0], image_point[1]

    def image_to_world(self, image_point, depth=1):
        """Transforms an image point to a world point using a pseudo-inverse of the P matrix."""
        assert self.P is not None, "Compute DLT before using transformations."

        M = self.P[:, :3]
        m4 = self.P[:, 3]

        image_point_homogeneous = np.append(image_point, 1)
        world_point = np.dot(np.linalg.pinv(M), (image_point_homogeneous - m4) * depth)
        return tuple(world_point)