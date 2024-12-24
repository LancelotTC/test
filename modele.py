from attrs import define, field
from random import choice
from enum import Enum


@define
class Player:
    name: str
    balance: int  # Solde du joueur
    current_tile: 'Tile'  # Case actuelle du joueur
    properties: list = field(factory=list)  # Liste des propriétés possédées
    nb_doubles: int = 0  # Compteur de doubles lors des lancers de dés

    def get_name(self) -> str:
        return self.name

    def get_balance(self) -> int:
        return self.balance

    def add_balance(self, amount: int) -> None:
        # Ajoute un montant au solde du joueur
        self.balance += amount

    def deduct_balance(self, amount: int) -> None:
        # Retire un montant du solde du joueur
        self.balance -= amount

    def get_current_tile(self) -> 'Tile':
        # Retourne la case du joueur
        return self.current_tile

    def set_current_tile(self, tile: 'Tile') -> None:
        # Définit la case actuelle du joueur
        self.current_tile = tile

    def buy_property(self) -> bool:
        # Permet au joueur d'acheter une propriété si les conditions sont remplies
        if isinstance(self.current_tile, PropertyTile) and self.current_tile.owner is None:
            if self.balance >= self.current_tile.price:
                # Déduit le prix de la propriété et assigne le joueur comme propriétaire
                self.deduct_balance(self.current_tile.price)
                self.current_tile.owner = self
                self.properties.append(self.current_tile)
                return True
        return False

    def sell_property(self, property_tile: 'PropertyTile') -> bool:
        # Permet au joueur de vendre une propriété possédée
        if property_tile in self.properties:
            # Si c'est une propriété avec des maisons, les maisons sont vendues
            if isinstance(property_tile, MultipleProperty) and property_tile.nb_houses > 0:
                self.add_balance(property_tile.house_price * property_tile.nb_houses)
                property_tile.nb_houses = 0
            # Ajoute le prix de la propriété au solde et libère la propriété
            self.add_balance(property_tile.price)
            property_tile.owner = None
            self.properties.remove(property_tile)
            return True
        return False

    def buy_house(self, property_tile: 'MultipleProperty', nb_houses: int) -> bool:
        # Permet au joueur d'acheter des maisons sur une propriété
        if nb_houses <= 4:
            # Vérifie si le joueur possède toutes les propriétés de la même couleur
            color_properties = [
                prop for prop in self.properties
                if isinstance(prop, MultipleProperty) and prop.color == property_tile.color
            ]
            required_properties = [
                prop for prop in PropertyTile.instances if isinstance(prop, MultipleProperty) and prop.color == property_tile.color
            ]
            if len(color_properties) == len(required_properties):
                # Vérifie si le joueur a suffisamment d'argent pour acheter les maisons
                total_cost = property_tile.house_price * nb_houses
                if self.balance >= total_cost:
                    # Déduit le coût total et ajoute les maisons à la propriété
                    self.deduct_balance(total_cost)
                    property_tile.nb_houses += nb_houses
                    return True
        return False

    def sell_house(self, property_tile: 'MultipleProperty', nb_houses: int) -> bool:
        # Permet au joueur de vendre des maisons sur une propriété
        if property_tile.nb_houses >= nb_houses:
            total_gain = property_tile.house_price * nb_houses
            self.add_balance(total_gain)
            property_tile.nb_houses -= nb_houses
            return True
        return False


@define
class Tile:
    # Représente une case du plateau
    name: str
    next: 'Tile'  # Case suivante
    previous: 'Tile'  # Case précédente
    players: list = field(factory=list)  # Liste des joueurs sur la case

    def get_name(self) -> str:
        return self.name

    def get_next(self) -> 'Tile':
        return self.next

    def get_previous(self) -> 'Tile':
        return self.previous

    def get_players(self) -> list:
        # Retourne la liste des joueurs présents sur la case
        return self.players

    def add_player(self, player: Player) -> None:
        # Ajoute un joueur sur la case
        self.players.append(player)


@define
class PropertyTile(Tile):
    # Représente une propriété
    price: int  # Prix de la propriété
    owner: Player = None  # Propriétaire de la propriété


@define
class MultipleProperty(PropertyTile):
    # Propriété pouvant obtenir des maisons
    color: 'Color'  # Couleur de la propriété
    house_price: int  # Prix d'une maison
    nb_houses: int = 0  # Nombre de maisons construites

    def get_total_charges(self) -> int:
        # Calcule les charges en fonction des maisons (+25% par maison)
        return self.price // 10 + int(self.price * 0.25 * self.nb_houses)


@define
class SingleProperty(PropertyTile):
    # Propriété sans maison
    def get_total_charges(self) -> int:
        # Retourne le prix fixe
        return self.price // 10


class Color(Enum):
    # Énumération des couleurs de propriétés
    BROWN = "brown"
    LIGHTBLUE = "lightblue"
    PINK = "pink"
    ORANGE = "orange"
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"


class Card(Enum):
    # Énumération des cartes chance
    OUTOFJAIL = "OUTOFJAIL"
    GOTOSTART = "GOTOSTART"
    GOTONEXTSTATION = "GOTONEXTSTATION"
    BANKBONUS = "BANKBONUS"
    GOBACK3TILES = "GOBACK3TILES"
    PAYTAX = "PAYTAX"
    GOTOPRISON = "GOTOPRISON"
    PAYSPEEDINGTICKET = "PAYSPEEDINGTICKET"


@define
class LuckTile(Tile):
    # Case Chance
    def draw_card(self) -> Card:
        # Tire une carte chance aléatoire
        return choice(list(Card))


@define
class JailTile(Tile):
    # Case Prison (sans logique dans le modèle)
    pass


@define
class PublicTile(Tile):
    # Case publique (sans logique dans le modèle)
    pass
