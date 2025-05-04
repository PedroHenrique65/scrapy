import scrapy

class NotebookSpider(scrapy.Spider):
    name = "notebook"
    allowed_domains = ["lista.mercadolivre.com.br", "mercadolivre.com.br"]
    start_urls = ["https://lista.mercadolivre.com.br/celular?sb=rb#D[A:celular]"]
    page_count = 1
    max_page = 10

    def parse(self, response):
        products = response.css('div.ui-search-result__wrapper')

        for product in products:
            prices = product.css('span.andes-money-amount__fraction::text').getall()
            
            product_link = product.css('a.poly-component__title::attr(href)').get()
            
            if product_link:
                yield scrapy.Request(
                    url=product_link,
                    callback=self.parse_product_details,
                    meta={
                        'brand': product.css('span.poly-component__brand::text').get(),
                        'nome': product.css('a.poly-component__title::text').get(),
                        'seller': product.css('span.poly-component__seller::text').get(),
                        'reviews_rating_number': product.css('span.poly-reviews__rating::text').get(),
                        'reviews_amount': product.css('span.poly-reviews__total::text').get(),
                        'old_money': prices[0] if len(prices) > 0 else None,
                        'new_money': prices[1] if len(prices) > 1 else None,
                    }
                )
            else:
                yield {
                    'brand': product.css('span.poly-component__brand::text').get(),
                    'nome': product.css('a.poly-component__title::text').get(),
                    'seller': product.css('span.poly-component__seller::text').get(),
                    'reviews_rating_number': product.css('span.poly-reviews__rating::text').get(),
                    'reviews_amount': product.css('span.poly-reviews__total::text').get(),
                    'old_money': prices[0] if len(prices) > 0 else None,
                    'new_money': prices[1] if len(prices) > 1 else None,
                    'titulo_pagina': None,
                    'anatel_number': None,
                    'marca': None
                }

        # Paginação
        if self.page_count < self.max_page:
            next_page = response.css('li.andes-pagination__button--next a::attr(href)').get()
            if next_page:
                self.page_count += 1
                yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_product_details(self, response):
        """Extrai dados adicionais da página do produto."""
        item_data = response.meta
        
        titulo_pagina = response.css('h1.ui-pdp-title::text').get(default='').strip()
        
        # Inicializa as variáveis
        anatel_number = None
        marca = None
        
        # Procura em todas as linhas da tabela de especificações
        for row in response.css('tr.ui-vpp-striped-specs__row'):
            # Extrai o cabeçalho (está dentro de um div dentro do th)
            header = row.css('th.andes-table__header div::text').get('').strip()
            
            # Extrai o valor (está dentro de um span com classe andes-table__column--value)
            value = row.css('td span.andes-table__column--value::text').get('').strip()
            
            if "Número de homologação da Anatel" in header:
                anatel_number = value
            elif "Marca" == header:
                marca = value
            
            # Se ambos foram encontrados, podemos parar
            if anatel_number and marca:
                break
        
        # Adiciona os novos campos
        item_data.update({
            'titulo_pagina': titulo_pagina,
            'anatel_number': anatel_number,
            'marca': marca
        })
        
        yield item_data