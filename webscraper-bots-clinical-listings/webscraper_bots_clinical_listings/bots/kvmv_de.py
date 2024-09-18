#!python

from selenium.webdriver.common.keys import Keys
from webscraper_bots_clinical_listings.utils import normalise_space
from webscraper_bots_clinical_listings.driven_pages.kvmv_de import SearchPage
from lxml.html import fromstring as etree
from lxml.etree import XPath
from time import sleep
import csv


def _get_extractor(treestruct):
    name = XPath(
        '//div[@class="ases-arzt-name-fachgebiet-text"]/a/span/text()',
        smart_strings=False
    )
    expertise = XPath(
        '//div[@class="ases-arzt-name-fachgebiet-text"]'
        '/a/text()[normalize-space()]',
        smart_strings=False
    )
    method = XPath(
        '//div[@class="ases-arzt-zusatzinfos"]/div/ul/li'
        '/b[contains(text(), "Therapieverfahren:")]'
        '/following-sibling::text()[normalize-space()]',
        smart_strings=False
    )
    lang = XPath(
        '//div[@class="ases-arzt-zusatzinfos"]/div/ul/li'
        '/b[contains(text(), "Fremdsprachen:")]'
        '/following-sibling::text()[normalize-space()]',
        smart_strings=False
    )
    add_desig = XPath(
        '//div[@class="ases-arzt-zusatzinfos"]/div/ul/li'
        '/b[contains(text(), "Zusatzbezeichnungen:")]'
        '/following-sibling::text()[normalize-space()]',
        smart_strings=False
    )
    add_act = XPath(
        '//div[@class="ases-arzt-zusatzinfos"]/div/ul/li'
        '/b[contains(text(), "Zusatzangebote:")]'
        '/following-sibling::text()[normalize-space()]',
        smart_strings=False
    )
    add_cont = XPath(
        '//div[@class="ases-arzt-zusatzinfos"]/div/ul/li'
        '/b[contains(text(), "Zusatzverträge:")]'
        '/following-sibling::text()[normalize-space()]',
        smart_strings=False
    )

    street = XPath(
        '//ul[@role="tablist"]/li[@role="tab" and '
            'position() = $subentry_index]'
        '/a/div/input[@class="ases-selector-hidden-arzt"]'
        '/@data-leistungsort-strasse',
        smart_strings=False
    )
    ZIP = XPath(
        '//ul[@role="tablist"]/li[@role="tab" and '
            'position() = $subentry_index]'
        '/a/div/input[@class="ases-selector-hidden-arzt"]'
        '/@data-leistungsort-plz',
        smart_strings=False
    )
    city = XPath(
        '//ul[@role="tablist"]/li[@role="tab" and '
            'position() = $subentry_index]'
        '/a/div/input[@class="ases-selector-hidden-arzt"]'
        '/@data-leistungsort-ort',
        smart_strings=False
    )
    contact = XPath(
        './/i[contains(@class, "fa-phone")]'
        '/following-sibling::text()[normalize-space()]',
        smart_strings=False
    )

    prac_form = XPath(
        './/div[@class="ases-leistungsort-kontaktdaten-header"]'
        '/following-sibling::ul[1]/li[1]/text()',
        smart_strings=False
    )
    assoc = XPath(
        './/div[@class="ases-leistungsort-kontaktdaten-header"]'
        '/following-sibling::ul[1]/li[2]/text()',
        smart_strings=False
    )
    focus = XPath(
        './/div[@class="ases-leistungsort-taetigkeit"]/ul/li'
        '/b[contains(text(),"Schwerpunkte:")]'
        '/following-sibling::text()[normalize-space()]',
        smart_strings=False
    )
    more_act = XPath(
        './/div[@class="ases-leistungsort-taetigkeit"]/ul/li'
        '/b[contains(text(),"Zusatzangebote:")]'
        '/following-sibling::text()[normalize-space()]',
        smart_strings=False
    )

    subentries = XPath('//div[@class="ui-tabs-panels"]/div[@role="tabpanel"]')

    if treestruct == 'arzt':
        hours_table_days = XPath(
            './/div[@class="ases-leistungsort-oeffnungszeiten-table"]'
            '/div[contains(@class, "ases-oeff-tag")]',
            smart_strings=False
        )
        day_name = XPath(
            './span[@class="ases-oeff-tag-name"]/text()',
            smart_strings=False
        )
        timings = XPath(
            './div[@class="ases-oeff-zeiten-list"]'
            '/div[@class="ases-oeff-block"]'
        )

    elif treestruct == 'psychotherapeut':
        hours_table_days = XPath(
            './/div[@class="ases-lo-te-header"]'
            '/following-sibling::div[1]/div'
            '/table/tbody/tr',
            smart_strings=False
        )
        day_name = XPath(
            './td[@class="ases-te-data-table-day"]/div/text()'
        )
        timings = XPath(
            './td[@class="ases-te-data-table-te-time"]/label'
        )

    def extract(entry):
        name_ = name(entry)[0]
        expertise_ = '; '.join(e.strip() for e in expertise(entry))

        lang_ = lang(entry)
        lang_ = normalise_space(lang_[0]) if lang_ else ''

        add_desig_ = add_desig(entry)
        add_desig_ = normalise_space(add_desig_[0]) if add_desig_ else ''

        add_act_ = add_act(entry)
        add_act_ = normalise_space(add_act_[0]) if add_act_ else ''

        add_cont_ = add_cont(entry)
        add_cont_ = normalise_space(add_cont_[0]) if add_cont_ else ''

        method_ = method(entry)
        method_ = normalise_space(method_[0]) if method_ else ''

        for i, subentry in enumerate(subentries(entry)):
            street_ = street(entry, subentry_index=i+1)[0]
            ZIP_ = ZIP(entry, subentry_index=i+1)[0]
            city_ = city(entry, subentry_index=i+1)[0]

            contact_ = dict(
                c.split(':', maxsplit=1)
                for c in contact(subentry)
            )
            phone = contact_.get('Tel.', '').strip()
            fax = contact_.get('Fax', '').strip()
            email = contact_.get('E-Mail', '').strip()

            hours = []
            for day in hours_table_days(subentry):
                day_name_ = day_name(day)
                day_name_ = day_name_[0] if day_name_ else 'Unavailable'
                timings_  = timings(day)
                timings_ = ', '.join(
                    normalise_space(t.xpath('string()'))
                    for t in timings_
                )
                hours.append(f'{day_name_} {timings_}')
            hours = ' | '.join(hours)

            prac_form_ = prac_form(subentry)
            prac_form_ = prac_form_[0].strip() if prac_form_ else ''

            assoc_ = assoc(subentry)
            assoc_ = assoc_[0].strip() if assoc_ else ''

            focus_ = focus(subentry)
            focus_ = normalise_space(focus_[0]) if focus_ else ''

            more_act_ = more_act(subentry)
            add_act_ += ((', ' if add_act_ else '')
                         + normalise_space(more_act_[0])
                        ) if more_act_ else ''

            yield (name_, expertise_, lang_, add_desig_, add_act_,
                   add_cont_, street_, ZIP_, city_, phone, fax, email,
                   hours, prac_form_, assoc_, focus_, method_)

    return extract


def main(search, dataf):
    extract = _get_extractor(search)
    fields = [
        'Name', 'Fachgebiet', 'Fremdsprachen', 'Zusatzbezeichnungen',
        'Zusatzangebote', 'Zusatzverträge', 'Strasse', 'PLZ', 'Ort',
        'Telefon', 'Telefax', 'Email', 'Sprechstunde', 'Praxisform',
        'BAG mit', 'Schwerpunkte', 'Therapieverfahren'
    ]

    with open(dataf, mode='x', newline='', encoding='utf-8') as dataf, \
         SearchPage(search=search) as searchpage:

        def extract_resultset():
            for entry in searchpage.iterate_results():
                html = entry.get_property('innerHTML')
                writer.writerows(extract(etree(html)))

        writer = csv.writer(dataf)
        writer.writerow(fields)

        sleep(3)
        searchpage.select(css='#overviewMapInputText').send_keys(Keys.ENTER)
        sleep(3)

        searchpage.select(
            xpath=\
            '//div[@class="ases-aggregation-box-attribut" and h2/text()="Praxisort"]'
            '//div[contains(@class, "ases-aggregation-filter-element-expand")]'
        ).click()
        sleep(5)
        locs = [elm.get_property('innerText') for elm in searchpage.select(
            xpath=\
            '//div[@class="ases-aggregation-box-attribut" and h2/text()="Praxisort"]'
        ).find_elements_by_class_name('ases-aggregation-filter-key')]

        # Some categories in this criteria are comprised of
        # other, more specific categories.
        superfluous_locs = [
            c for c in locs if sum(
                c is not p and c in p  # c is the candidate being tested
                for p in locs          # and p -- one of the peers.
            )
        ]

        for i, loc, icount in searchpage.iterate_results_categories('Praxisort'):
            if loc in superfluous_locs:
                continue
            if icount > 100:
                for j, expertise, jcount in \
                searchpage.iterate_results_categories('Fachgebiet'):
                    searchpage.maximise_page_size()
                    extract_resultset()
            else:
            	searchpage.maximise_page_size()
            	extract_resultset()


if __name__ == '__main__':
    import sys
    import getopt

    opts, args = getopt.getopt(
        sys.argv[1:], 'o:',
        ['output=', 'arztsuche', 'psychotherapeutensuche']
    )
    opts = dict(opts)

    dataf = 'kvmv_de_arzt_data.csv'
    search = 'arzt'
    if '--psychotherapeutensuche' in opts.keys():
        search = 'psychotherapeut'
        dataf = 'kvmv_de_psychotherapeut_data.csv'
    if '--output' in opts.keys():
        dataf = opts['--output']

    main(search, dataf)

