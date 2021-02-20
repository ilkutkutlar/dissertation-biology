import numpy as np


class StructuredResults:
    """
    :param np.ndarray unstructured_results: results
    :param List[str] names_of_species: in the results
    """

    def __init__(self, unstructured_results, names_of_species, time_space):

        self.species = StructuredResults.label_results(unstructured_results, names_of_species)
        self.time_space = time_space

    """
    Return results between the given times
    :param str species: The name of the species for which results will be returned.
    :param float t1: The lower bound for time period
    :param float t2: The uppor bound for time period
    """

    def results_between_times(self, species, t1, t2):
        results = list()

        i = 0
        for x in self.time_space:
            if t1 <= x <= t2:
                results.append(self.species[species][i])
            i += 1

        return results

    """
    Return a dictionary of unstructured results where key: species name, value: unstructured results for the species
    :param np.ndarray results: Raw, unstructured results output by np.odeint.
    :param List[str] labels: The labels to use for labeling the unstructured results
    :returns Dict[str, np.ndarray] of key: species name, value: unstructured result
    """

    @staticmethod
    def label_results(results, labels):
        labeled_results = dict()

        # Attach species names to results
        for i, s in enumerate(labels):
            # Syntax meaning: a list consisting of the ith element of each list in results
            labeled_results[s] = results[:, i]

        return labeled_results
