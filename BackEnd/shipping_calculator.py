import requests
import json
from typing import Optional

class ShippingCalculator:
    """Calculadora de frete usando CEP de origem e destino"""
    
    ORIGIN_CEP = "24210001"  # CEP de origem fixo
    
    @staticmethod
    def calculate_shipping(destination_cep: str, weight: float = 0.5) -> Optional[float]:
        """
        Calcula o valor do frete baseado no CEP de destino
        
        Args:
            destination_cep: CEP de destino
            weight: Peso em kg (padrão: 0.5kg para CDs)
            
        Returns:
            Valor do frete em reais ou None se não conseguir calcular
        """
        try:
            # Remove caracteres não numéricos do CEP
            origin_clean = ''.join(filter(str.isdigit, ShippingCalculator.ORIGIN_CEP))
            destination_clean = ''.join(filter(str.isdigit, destination_cep))
            
            # Validação básica de CEP
            if len(origin_clean) != 8 or len(destination_clean) != 8:
                return None
            
            # Para simplificar, vamos usar uma tabela de valores baseada na região
            # Em uma implementação real, você usaria a API dos Correios
            return ShippingCalculator._calculate_by_region(destination_clean, weight)
            
        except Exception as e:
            print(f"Erro ao calcular frete: {e}")
            return None
    
    @staticmethod
    def _calculate_by_region(destination_cep: str, weight: float) -> float:
        """
        Calcula frete baseado na região do CEP
        Valores aproximados baseados em regiões do Brasil
        """
        try:
            # Extrai os dois primeiros dígitos para identificar a região
            region_code = int(destination_cep[:2])
            
            # Tabela de valores por região (dois primeiros dígitos do CEP)
            # Valores em reais para peso padrão de 0.5kg
            shipping_rates = {
                # Região Sudeste (SP, RJ, ES, MG)
                **{i: 15.00 for i in range(1, 20)},    # SP
                **{i: 12.00 for i in range(20, 29)},   # RJ (origem)
                **{i: 18.00 for i in range(29, 30)},   # ES
                **{i: 20.00 for i in range(30, 40)},   # MG
                
                # Região Sul (PR, SC, RS)
                **{i: 25.00 for i in range(80, 88)},   # PR
                **{i: 28.00 for i in range(88, 90)},   # SC
                **{i: 30.00 for i in range(90, 100)},  # RS
                
                # Região Nordeste
                **{i: 35.00 for i in range(40, 49)},   # BA
                **{i: 40.00 for i in range(50, 57)},   # PE
                **{i: 38.00 for i in range(57, 59)},   # AL
                **{i: 42.00 for i in range(59, 64)},   # PB, RN
                **{i: 45.00 for i in range(60, 64)},   # CE
                **{i: 40.00 for i in range(64, 65)},   # PI
                **{i: 48.00 for i in range(65, 66)},   # MA
                
                # Região Norte
                **{i: 50.00 for i in range(66, 69)},   # PA
                **{i: 55.00 for i in range(69, 70)},   # AC
                **{i: 52.00 for i in range(70, 73)},   # DF, GO
                **{i: 45.00 for i in range(73, 78)},   # TO, MT
                **{i: 60.00 for i in range(78, 79)},   # RO
                **{i: 65.00 for i in range(79, 80)},   # RR
                
                # Região Centro-Oeste
                **{i: 35.00 for i in range(70, 73)},   # DF
                **{i: 40.00 for i in range(73, 78)},   # GO, TO
                **{i: 45.00 for i in range(78, 79)},   # MT
                **{i: 50.00 for i in range(79, 80)},   # MS
            }
            
            base_rate = shipping_rates.get(region_code, 35.00)  # Valor padrão
            
            # Ajuste por peso (para cada 0.1kg adicional, acrescenta 10% do valor base)
            weight_multiplier = 1 + max(0, (weight - 0.5) * 0.2)
            
            final_rate = base_rate * weight_multiplier
            
            return round(final_rate, 2)
            
        except Exception as e:
            print(f"Erro ao calcular frete por região: {e}")
            return 35.00  # Valor padrão em caso de erro

    @staticmethod
    def get_estimated_delivery_days(destination_cep: str) -> int:
        """
        Retorna estimativa de dias úteis para entrega
        """
        try:
            destination_clean = ''.join(filter(str.isdigit, destination_cep))
            region_code = int(destination_clean[:2])
            
            # Estimativa de dias por região
            delivery_days = {
                # Sudeste - mais próximo
                **{i: 3 for i in range(1, 40)},
                
                # Sul
                **{i: 5 for i in range(80, 100)},
                
                # Nordeste
                **{i: 7 for i in range(40, 66)},
                
                # Norte
                **{i: 10 for i in range(66, 70)},
                **{i: 12 for i in range(78, 80)},
                
                # Centro-Oeste
                **{i: 6 for i in range(70, 78)},
            }
            
            return delivery_days.get(region_code, 7)  # Padrão: 7 dias
            
        except Exception:
            return 7  # Valor padrão
