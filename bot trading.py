import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from binance import Client

api_key = 'AHAH'
api_secret = 'AHAH'
client = Client(api_key, api_secret)

def create_segments(min_price, max_price, segment_size):
    """
    Crée des segments de prix pour le trading.

    Args:
        min_price (float): Prix minimum
        max_price (float): Prix maximum
        segment_size (float): Taille de chaque segment de prix

    Returns:
        list: Liste de segments de prix, où chaque segment est un tuple (lower_bound, upper_bound)
    """
    segments = []
    current_price = min_price
    while current_price < max_price:
        segments.append((current_price, current_price + segment_size))
        current_price += segment_size
    return segments

def bot_behavior(segment, current_price, balance, frais, crypto_balance):
    """
    Définit le comportement du bot de trading en fonction du segment de prix actuel et du prix courant.

    Args:
        segment (tuple): Segment de prix actuel (lower_bound, upper_bound)
        current_price (float): Prix courant du marché
        balance (float): Solde du compte
        frais (float): Frais de transaction
        crypto_balance (float): Solde de crypto-monnaie

    Returns:
        tuple: ('buy', sell_price) si le bot doit acheter, ('sell', None) si le bot doit vendre, ('hold', None) sinon
    """
    lower_bound, upper_bound = segment
    if lower_bound <= current_price <= upper_bound:
        if balance > 0:
            buy_price = current_price
            sell_price = buy_price * (1 + frais)
            many = balance / buy_price
            order = client.create_order(
                symbol='BNBUSDT',
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=Client.TIME_IN_FORCE_GTC,
                quantity=many,
                price=buy_price
            )
            return 'buy', sell_price
        elif crypto_balance > 0:
            sell_price = current_price
            many = crypto_balance
            order = client.create_order(
                symbol='BNBUSDT',
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=Client.TIME_IN_FORCE_GTC,
                quantity=many,
                price=sell_price
            )
            return 'sell', None
    return 'hold', None

min_price = float(input("Entrez le prix minimum: "))
max_price = float(input("Entrez le prix maximum: "))
segment_size = 0.1

segments = create_segments(min_price, max_price, segment_size)
print("Segments de prix:", segments)

crypto_balance = 0.0
for segment in segments:
    current_price = (segment[0] + segment[1]) / 2  
    balance = 100.0 
    frais = 0.001 
    action, sell_price = bot_behavior(segment, current_price, balance, frais, crypto_balance)
    if action == 'buy':
        crypto_balance += balance / current_price
        balance = 0.0
    elif action == 'sell':
        balance += crypto_balance * current_price
        crypto_balance = 0.0
    print(f"Segment {segment}: {action} à {sell_price:.2f} si balance > 0")
    print(f"Balance: {balance:.2f}, Crypto Balance: {crypto_balance:.2f}")
