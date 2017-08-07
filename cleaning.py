# -*- coding: utf-8 -*-

import re
import numpy as np

def detect_separator(ingredients):
    num_commas = len(re.findall(u'\,',ingredients))
    num_slash = len(re.findall(r'\\',ingredients))
    num_fwdslash = len(re.findall(u'\/',ingredients))
    num_pipe = len(re.findall(u'\|',ingredients))
    num_dash = len(re.findall(u'\-',ingredients))
    num_semicolon = len(re.findall(u'\;',ingredients))
    num_dot = len(re.findall(u'•',ingredients))
    num_ing = len(re.findall(u'ingredients',ingredients))
    del_list = [u',',r'\\',u'/',u'|',u'-',u';',u'•',u'ingredients']
    totals = [num_commas,num_slash,num_fwdslash,num_pipe,num_dash,num_semicolon,num_dot,num_ing]
    if np.any(totals):
        m = np.argmax(np.array(totals))
        return del_list[m]
    else:
        return None
    
def parse_parens(ingredient):
    #there's an intermediate paren group with surrounding spaces
    #but there could be no text after the paren group
    cleaned_list = []
    match = re.search(u'(.+)\s\((.+)\)\s?(.+)?',ingredient) 
    if match:
        subingredient = match.group(1)
        if match.group(3)!=None:
            subingredient = match.group(1) + u' ' + match.group(3)
        cleaned_list.append(subingredient.strip())
        subingredient = match.group(2)
        if match.group(3)!=None:
            subingredient = match.group(2) + u' ' + match.group(3)
        cleaned_list.append(subingredient.strip())
        return cleaned_list
    return [ingredient.strip()]

def clean_ingredients(ingredients):
    if ingredients=='Alcohol DenatHydrofluorocarbon 152AButaneIsobutanePropaneFragrance (Parfum)':
        return ['alcohol denat','hydrofluorocarbon 152A','butane','isobutane','propane','fragrance']
    else:
        ingredients = ingredients.lower()
        match = re.search('(.+?)legal\s+disclaimer',ingredients)
        if match:
            ingredients = match.group(1) 
        killwords = ['patent pending',
                     'Note: Below Is The Most Comprehensive Ingredient List For This Product, But Please Note That Ingredients Vary By Shade.Please Check The Box At The Store For An Ingredient List At The Shade Level.'.lower(),
                     'Our formulas are modified from time to time, so this ingredient listing may not exactly reflect the ingredients in the product you purchase and use. Always read the ingredient list on the product label before use.'.lower(),
                     'Full disclosure ingredients according to PCPC standards'.lower(),
                     '(90%',
                     "Ingredients are subject to change at the manufacturer's discretion. For the most complete and up-to-date list of ingredients, refer to the product packaging".lower(),
                     u'Crème Colorant Ingredeints:'.lower(),
                     u'Developer Crème Ingredients:'.lower(),
                     'non-medicinal',
                     'active ingredient - purpose.',
                     ' which has been fda approved for more than 30 years',
                     'neutrogena original facial bar 3.5 oz (pack of 6)',
                     'see package for product ingredients',
                     'soothing formula of ',
                     'please see individual products for ingredients',
                     'see box',
                     'vary by color',
                     'see product packaging',
                     'false',
                     'no active ingredients',
                     'ingredients not available at this time',
                     'see package for product detailes',
                     'see package for product ingredients',
                     'see product photo',
                     'see product photos',
                     'inactive ingredients:',
                     '- anti-perspirant',
                     'anti-perspirant',
                     'shampoo:',
                     'conditioner:',
                     'purpose',
                     'relaxer',
                     'base',
                     'leave-in',
                     'active ingredient:',
                     'active ingredients:',                 
                     'super strength activator',
                     'herbal infusion',
                     '*',
                     '^',
                     'ingredients:',
                     'and ',
                     'contains ',                 
                     'colorant',
                     'cream',
                     'developer',
                     'color',
                     'after'
                     'inactive:',
                     'active:'
                     'n/a']
        for killword in killwords:
            ingredients = ingredients.replace(killword,'')
        ingredients = ingredients.strip()
        nums = re.findall('\([\d+\.\,\\\/\|\%]*\)', ingredients)
        for num in nums:
            ingredients = ingredients.replace(num,'') # remove numbers in parentheses
        cleaned_list = {}            
        if 'N,N-Bis(2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower() in ingredients:
            cleaned_list['N,N-Bis(2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower()]=1
            ingredients = ingredients.replace('N,N-Bis(2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower(),'')
        if 'N,N-Bis (2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower() in ingredients:
            cleaned_list['N,N-Bis(2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower()]=1
            ingredients = ingredients.replace('N,N-Bis (2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower(),'')
        if 'N, N-BIS(2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower() in ingredients:
            cleaned_list['N,N-Bis(2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower()]=1
            ingredients = ingredients.replace('N, N-BIS(2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower(),'')
        if 'N, n-bis (2-hydroxyethyl), P-Phenylenediamine Sulfate'.lower() in ingredients:
            cleaned_list['N,N-Bis(2-Hydroxyethyl)-P-Phenylenediamine Sulfate'.lower()]=1
            ingredients = ingredients.replace('N, n-bis (2-hydroxyethyl), P-Phenylenediamine Sulfate'.lower(),'')   
        sep = detect_separator(ingredients)
        if sep!=None:
            ingredients = ingredients.replace(u'.',sep) # change periods into the default separator
            ingredient_list = ingredients.split(sep)
        elif ' ' in ingredients:
            ingredient_list = ingredients.split(' ')
            if len(ingredient_list)<6 and not 'fragrance' in ingredient_list:
                ingredient_list = [' '.join(ingredient_list)]
        else:
            ingredient_list = [ingredients]
        for ingredient in ingredient_list:
            if 'water' in ingredient:
                cleaned_list[u'water']=1
            elif 'fragrance' in ingredient:
                cleaned_list[u'fragrance']=1
            else:
                lil_list = parse_parens(ingredient)
                for item in lil_list:
                    cleaned_list[item]=1
        if 'aqua' in cleaned_list:
            del cleaned_list['aqua']
            cleaned_list[u'water']=1
        if 'eau' in cleaned_list:
            del cleaned_list['eau']
            cleaned_list[u'water']=1
        if '' in cleaned_list:
            del cleaned_list['']
        if 'parfum' in cleaned_list:
            del cleaned_list['parfum']
            cleaned_list[u'fragrance']=1
        if 'f' in cleaned_list:
            del cleaned_list['f'] 
        if 'i' in cleaned_list:
            del cleaned_list['i']
        if 'l' in cleaned_list:
            del cleaned_list['l']     
        return list(cleaned_list.keys())