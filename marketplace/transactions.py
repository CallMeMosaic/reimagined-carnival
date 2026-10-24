"""Übersicht über den Dateiinhalt:

Implementiert die Dataclass `Transaction` und die Hashtabellen-Klasse `Transactions`
zur Erfassung und Zählung von Kaufabwicklungs-Transaktionen und Hash-Kollisionen.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class Transaction:
    """
    Transaction implements a HashTable as a List of Lists.
    Since it uses standard Python lists, which are mutable and dynamic in size per default.
    Due to how Lists in Python are implemented, all operations (except printing all elements or searching through it) are
    Θ(1), as they can be accessed instantaneously. Same goes for adding items to the "slots" or "buckets", these expand
    dynamically with the amount of data stored in them (initially they are empty). Adding items to these lists is also always
    Θ(1). The size of the HashTable is given as a parameter by the user or defaults to 128.

    Attributes:
        seller (str): Name des Verkäufers.
        buyer (str): Name des Käufers.
        price (float): Verkaufspreis in Euro.
        timestamp (datetime): Zeitstempel der Transaktion.
        product_name (str): Name des verkauften Produkts.
    """
    seller: str
    buyer: str
    price: float
    timestamp: datetime
    product_name: str

    def __repr__(self) -> str:
        """Gibt eine kompakte String-Repräsentation der Transaktion zurück.

        Args:
            None

        Returns:
            str: Formatierte Zeichenkette.

        Raises:
            None
        """
        # Compact representation for printing
        ts = self.timestamp.isoformat(timespec="seconds")
        return (f"Transaction(seller={self.seller!r}, buyer={self.buyer!r}, "
                f"price={self.price}, timestamp={ts}, product_name={self.product_name!r})")


class Transactions:
    """Hashtabelle zur Speicherung von Transaktionen und Erfassung von Hash-Kollisionen.

    Attributes:
        _capacity (int): Kapazität/Anzahl der Buckets der Hashtabelle.
        _buckets (List[List[Transaction]]): Liste der Buckets für Transaktionen.
        _size (int): Gesamtanzahl gespeicherter Transaktionen.
        _collisions (int): Gesamtzahl aufgetretener Hash-Kollisionen.
    """
    """
    Intentionally naive hash table
    - Uses a deliberately bad hash function (default: first letter of product name).
    - Counts total collisions since creation.
    """
    
    def __init__(self, capacity: int = 128) -> None:
        """Initialisiert die Transactions-Hashtabelle mit einer bestimmten Kapazität.

        Args:
            capacity (int): Kapazität (Anzahl Buckets). Defaults to 128.

        Raises:
            ValueError: Wenn `capacity` <= 0 ist.
        """
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity: int = capacity
        self._buckets: List[List[Transaction]] = [[] for _ in range(capacity)]
        self._size: int = 0
        self._collisions: int = 0

    # *** PUBLIC METHODS ***

    def insert(self, tx: Transaction) -> None:
        """Fügt eine Transaktion ein und zählt Kollisionen, wenn der Ziel-Bucket nicht leer ist.

        Args:
            tx (Transaction): Die einzufügende Transaktion.

        Returns:
            None

        Raises:
            None
        """
        idx = self._hash_fn(tx)
        bucket = self._buckets[idx]
        if len(bucket) > 0:
            self._collisions += 1
        bucket.append(tx)
        self._size += 1

    # *** PUBLIC GET METHODS ***

    def get_collisions(self) -> int:
        """Gibt die Gesamtzahl aufgetretener Kollisionen seit Erstellung zurück.

        Args:
            None

        Returns:
            int: Anzahl der Kollisionen.

        Raises:
            None
        """
        return self._collisions

    def get_capacity(self) -> int:
        """Gibt die Kapazität (Anzahl der Buckets) der Hashtabelle zurück.

        Args:
            None

        Returns:
            int: Kapazität der Hashtabelle.

        Raises:
            None
        """
        return self._capacity

    def get_size(self) -> int:
        """Gibt die Gesamtanzahl eingefügter Transaktionen zurück.

        Args:
            None

        Returns:
            int: Anzahl gespeicherter Transaktionen.

        Raises:
            None
        """
        return self._size

    # *** PRIVATE METHODS ***

    def _hash_fn(self, tx: Transaction) -> int:
        """
        Original Hashfunction:
            First checks if the transaction even has a product name, if that is not the case, the transaction is not
            valid and gets rejected (return 0).
            The HashTable itself is implemented as a List of Lists.
            The normal Hashfunction only looks at the first letter of the key, converts it to a lowercase letter.
            Since the lowercase letters map directly to the indicies 0 to 25 (standard english letters), in most cases
            only the first 25 buckets will be utilized and the rest of the table will stay empty, therefore wasting storage
            and causing a massive clustering.

        New Hashfunction:
            This function will take into account the entire name of the transaction and it's timestamp, and convert
            it to a number value using Python's build in hash() function.
            This approach is chosen, since the alternative (only name or timestamp) could result in clustering and
            doing both using ord() would result in unoptimized Θ(k+h) time complexity, where k ist the length of the
            product name and h ist the length of the timestamp. This is rather unoptimal and since Pythong's hash function is
            written in C and optimized to run efficiently, it will be used here.
            Then the function multiplies a prime number (7) in order to shift it reliably and then use the modulo of capacity to give it a designated index.


        :param tx:
        :return:
        """


        # Creates a Tuple object that the hash function can hash, since both variables have different types, adding them would result in a TypeError :c
        key = (f"{tx.seller}|{tx.buyer}|{tx.price}|"
               f"{tx.timestamp.isoformat()}|{tx.product_name}")
        h = 0
        for ch in key:
            h = (h * 31 + ord(ch)) % 2_147_483_647

        return h % self._capacity


