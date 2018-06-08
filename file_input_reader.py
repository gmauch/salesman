import argparse
import os
import time
import sys

class file_reader:
    def __init__(self, input_dir, extension, line_parser, report_generator):
        self.input_dir = input_dir
        self.extension = extension
        self.line_parser = line_parser
        self.report_generator = report_generator

    def keep_scanning_input_dir(self):
        try:
            already_processed_files = {}
            while True:
                for file in os.listdir(self.input_dir):
                    if file.endswith(self.extension) and not already_processed_files.get(file, False):
                        self.read_file(os.path.join(self.input_dir, file))
                        already_processed_files[file] =  True
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)

    def read_file(self, file_to_read):
        with open(file_to_read) as f:
            lines = f.readlines()

        for line in lines:
            self.report_generator.add_item(self.line_parser.parse_line(line))

        report = self.report_generator.generate_report()
        self.report_generator.write_report_to_output(report, os.path.basename(file_to_read))
        self.report_generator.clear()

class report_generator():
    OUTPUT_FILE_LOCATION = os.getcwd() + '/out/'
    OUTPUT_FILE_EXTENSION = '.done'
    def __init__(self):
        self.report_items = {}

    def clear(self):
        self.report_items = {}

    def add_item(self, item):
        item_list = self.report_items.get(item.get_type_id(), [])
        item_list.append(item)
        self.report_items[item.get_type_id()] = item_list

    def generate_report(self):
        lines_to_write = []
        lines_to_write.append(self.get_amount_of_clients())
        lines_to_write.append(self.get_amount_of_salesman())
        lines_to_write.append(self.get_id_of_most_expensive_sale())
        lines_to_write.append(self.get_worst_salesman())

        return lines_to_write

    def write_report_to_output(self, report, input_file):
        current_extension = os.path.splitext(input_file)[1]
        new_extension = '{}{}'.format(self.OUTPUT_FILE_EXTENSION, current_extension)
        output_file = input_file.replace(current_extension, new_extension)
        output_file_path = os.path.join(self.OUTPUT_FILE_LOCATION, output_file)
        with open(output_file_path, 'w') as out_file:
            for line in report:
                out_file.write(line)

    def get_amount_of_clients(self):
        return 'Amount of clients found: {}\n'.format(len(self.report_items.get(customer.TYPE_ID, [])))

    def get_amount_of_salesman(self):
        return 'Amount of salesmen found: {}\n'.format(len(self.report_items.get(salesman.TYPE_ID, [])))

    def get_id_of_most_expensive_sale(self):
        total_sales = self.report_items.get(sales.TYPE_ID, [])
        if len(total_sales) > 0:
            sales_items = []
            for sale in total_sales:
                for item in sale.items:
                    sales_items.append(item)

            sales_items.sort(key=lambda item: item.price, reverse=True)
            expensive_sale = sales_items[0]
            return 'Most expensive sale with price {} has ID {}\n'.format(expensive_sale.price, expensive_sale.id)
        else:
            return 'No sales have been found\n'

    def get_worst_salesman(self):
        # We can't be sure that high priced sales are better, because it depends on the profit % of the price
        # so the worst salesman is defined as the one with the less amount of sales, since a salesman's job is to sell!
        all_sales = self.report_items.get(sales.TYPE_ID, [])
        if len(all_sales) > 0:
            sales_by_salesman = {}
            for sale in all_sales:
                current_sales_count = sales_by_salesman.get(sale.name, 0) + 1
                sales_by_salesman[sale.name] = current_sales_count

            ordered_sales = sorted(sales_by_salesman.items(), key=lambda x: x[1])
            worst_salesman = ordered_sales[0]
            return 'Shame on {} who performed only {} sales!\n'.format(worst_salesman[0], worst_salesman[1]) #Hope not to be sued for that...
        else:
            return 'No sales have been found\n'


class line_parser_factory:
    def __init__(self, parsers, default_parser, token_separator, item_token_separator):
        self.parsers = parsers
        self.default_parser = default_parser
        self.token_separator = token_separator
        self.item_token_separator = item_token_separator

    def parse_line(self, line_to_parse):
        tokens = line_to_parse.split(self.token_separator)
        parser = self.get_parser_for_id(tokens[0])
        return parser.parse_line(line_to_parse)

    def get_parser_for_id(self, id):
        return self.parsers.get(id, self.default_parser)


class line_parser():
    def __init__(self, token_separator):
        self.token_separator = token_separator

    def parse_line(self, line):
        pass


class unknown_line_parser(line_parser):
    def parse_line(self, line):
        pass

class item:
    def get_type_id(self):
        return self.TYPE_ID


class salesman(item):
    TYPE_ID = '001'

    def __init__(self, cpf, Name, Salary):
        self.cpf = cpf
        self.Name = Name
        self.Salary = Salary


class customer(item):
    TYPE_ID = '002'

    def __init__(self, cnpj, Name, BusinessArea):
        self.cnpj = cnpj
        self.Name = Name
        self.BusinessArea = BusinessArea


class sales_items(item):
    def __init__(self, id, quantity, price):
        self.id = id
        self.quantity = quantity
        self.price = price


class sales(item):
    TYPE_ID = '003'
    def __init__(self, sale, id, name, items):
        self.sale = sale
        self.id = id
        self.name = name
        self.items = items


class salesman_line_parser(line_parser):
    def parse_line(self, line):
        tokens = line.split(self.token_separator)
        return salesman(tokens[1], tokens[2].strip('\n'), tokens[3])


class customer_line_parser(line_parser):
    def parse_line(self, line):
        tokens = line.split(self.token_separator)
        return customer(tokens[1], tokens[2].strip('\n'), tokens[3].strip('\n'))


class sales_line_item_parser(line_parser):
    def __init__(self, token_separator, item_token_separator, inter_item_token_separator):
        super().__init__(token_separator)
        self.item_token_separator = item_token_separator
        self.inter_item_token_separator = inter_item_token_separator

    def parse_line(self, line):
        items = []
        tokens = line.replace(self.inter_item_token_separator, self.item_token_separator).split(self.item_token_separator)
        for i in range(0, len(tokens) -1, 3):
            items.append(sales_items(tokens[i].strip('['), tokens[i+1], float(tokens[i+2].strip(']'))))

        return  items


class sales_line_parser(line_parser):
    def __init__(self, token_separator, item_token_separator, items_parser):
        super().__init__(token_separator)
        self.item_token_separator = item_token_separator
        self.items_parser = items_parser

    def parse_line(self, line):
        tokens = line.split(self.token_separator)
        items = self.items_parser.parse_line(tokens[2])
        return sales(tokens[0], tokens[1], tokens[3].strip('\n'), items)


class controller:
    def __init__(self, line_token_separator, items_token_separator, inter_items_token_separator, flat_file_extension, files_location):
        self.line_token_separator = line_token_separator
        self.items_token_separator = items_token_separator
        self.inter_items_token_separator = inter_items_token_separator
        self.files_location = files_location
        self.flat_file_extension = flat_file_extension

    def create_parser_factory(self):
        salesman_parser = salesman_line_parser(self.line_token_separator)
        customer_parser = customer_line_parser(self.line_token_separator)
        sales_items_parser = sales_line_item_parser(self.line_token_separator, self.items_token_separator,
                                                    self.inter_items_token_separator)
        sales_parser = sales_line_parser(self.line_token_separator, self.items_token_separator, sales_items_parser)
        default_parser = unknown_line_parser(self.line_token_separator)
        parsers = {salesman.TYPE_ID: salesman_parser,
                   customer.TYPE_ID: customer_parser,
                   sales.TYPE_ID: sales_parser}
        return line_parser_factory(parsers, default_parser, self.line_token_separator, self.items_token_separator)

    def create_reader(self, parser_factory, reporter):
        return file_reader(self.files_location, self.flat_file_extension, parser_factory, reporter)

    def start_reading_files(self):
        parser_factory = self.create_parser_factory()
        reporter = report_generator()
        file_processer = self.create_reader(parser_factory, reporter)
        file_processer.keep_scanning_input_dir()


class arguments:
    DEFAULT_LINE_TOKEN_SEPARATOR = 'ç'
    DEFAULT_ITEMS_TOKEN_SEPARATOR = '-'
    DEFAULT_INTER_ITEMS_TOKEN_SEPARATOR = ','
    DEFAULT_FLAT_FILE_EXTENSION = '.dat'
    DEFAULT_FILES_LOCATION = os.getcwd() + '/in/'

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Salesman challenge solution. This application implements a"
                                                          "data analysis tool that reads data files containing sales data. "
                                                          "Further definitions and goals can be found in docs/ folder.")

    def _configure_command_args(self):
        self.parser.add_argument("-ls", "--line_token_separator",
                                 help="Char that delimits tokens in a line. Defaults to {}".format(self.DEFAULT_LINE_TOKEN_SEPARATOR),
                                 type=str,
                                 default=self.DEFAULT_LINE_TOKEN_SEPARATOR)

        self.parser.add_argument("-it", "--item_token_separator",
                                 help="Char that delimits each item inside a sales data item. Defaults to {}".format(self.DEFAULT_ITEMS_TOKEN_SEPARATOR),
                                 type=str,
                                 default=self.DEFAULT_ITEMS_TOKEN_SEPARATOR)

        self.parser.add_argument("-ii", "--inter_item_token_separator",
                                 help="Char that delimits sales data items. Defaults to {}".format(self.DEFAULT_INTER_ITEMS_TOKEN_SEPARATOR),
                                 type=str,
                                 default=self.DEFAULT_INTER_ITEMS_TOKEN_SEPARATOR)

        self.parser.add_argument("-fe", "--file_extension",
                                 help="Extension of files to be read as input. Defaults to {}".format(self.DEFAULT_FLAT_FILE_EXTENSION),
                                 type=str,
                                 default=self.DEFAULT_FLAT_FILE_EXTENSION)

        self.parser.add_argument("-fl", "--file_location",
                                 help="Folder to be scanning for input files. Defaults to {}".format(self.DEFAULT_FILES_LOCATION),
                                 type=str,
                                 default=self.DEFAULT_FILES_LOCATION)

    def _parse_command_args(self):
        args = self.parser.parse_args()
        self.line_token_separator = args.line_token_separator
        self.item_token_separator = args.item_token_separator
        self.inter_item_token_separator = args.inter_item_token_separator
        self.file_extension = args.file_extension
        self.file_location = args.file_location

if __name__ == '__main__':

    args = arguments()
    args._configure_command_args()
    args._parse_command_args()

    controller = controller(args.line_token_separator,
                            args.item_token_separator,
                            args.inter_item_token_separator,
                            args.file_extension,
                            args.file_location)
    controller.start_reading_files()