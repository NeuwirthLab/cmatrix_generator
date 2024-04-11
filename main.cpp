#include <iostream>
#include <vector>
#include <random>
#include <type_traits>
#include <fstream>
#include <iomanip>
#include <getopt.h>
#include <filesystem>
#include "taco.h"

#define BENCHMARK
static int copy_flag = false;


template<typename T>
std::vector<std::vector<T> > generate_dense_matrix(int rows, int cols, int num_non_zero, int max_value) {
    std::vector<std::vector<T> > matrix(rows, std::vector<T>(cols, 0));
    std::random_device rd;
    std::mt19937 gen(rd());
    for (int i = 0; i < num_non_zero; ++i) {
        std::uniform_int_distribution<int> row_dist(0, rows - 1);
        std::uniform_int_distribution<int> col_dist(0, cols - 1);
        int row = row_dist(gen);
        int col = col_dist(gen);
        if (std::is_same<T, int>::value) {
            std::uniform_int_distribution<int> val_dist(0, max_value);
            matrix[row][col] = val_dist(gen);
        } else {
            std::uniform_real_distribution<T> val_dist(0, max_value);
            matrix[row][col] = val_dist(gen);
        }
    }
    return matrix;
}

template<typename T>
void write_dense_matrix_market_format(const std::vector<std::vector<T> > &matrix, const std::string &file_name) {
    std::ofstream file(file_name);
    file << "%%MatrixMarket matrix coordinate real general" << std::endl;
    file << matrix.size() << " " << matrix[0].size() << " " << matrix.size() * matrix[0].size() << std::endl;
    for (int i = 0; i < matrix.size(); ++i) {
        for (int j = 0; j < matrix[0].size(); ++j) {
            file << matrix[i][j] << std::endl;
        }
    }
    file.close();
}

void copy_file(const std::string &src, const std::string &dst) {
    std::ifstream src_file(src, std::ios::binary);
    std::ofstream dst_file(dst, std::ios::binary);
    dst_file << src_file.rdbuf();
}


std::ifstream::pos_type get_filesize(const char *filename) {
    std::ifstream in(filename, std::ifstream::ate | std::ifstream::binary);
    return in.tellg();
}

std::string get_file_name_from_rows_and_cols(int rows, int cols, bool is_dense) {
    if (is_dense) {
        return "dense_matrix_" + std::to_string(rows) + "x" + std::to_string(cols) + ".mtx";
    } else {
        return "sparse_matrix_" + std::to_string(rows) + "x" + std::to_string(cols) + ".mtx";
    }
}

int main(int argc, char *argv[]) {
    std::filesystem::path write_file_path{};
    std::filesystem::path read_file_path{};
    int cols, rows;
    const char *const short_opts = "i:o:c:r:";
    static const struct option long_opts[] = {
            {"input",   required_argument, nullptr, 'i'},
            {"output",  required_argument, nullptr, 'o'},
            {"cols",    required_argument, nullptr, 'c'},
            {"rows",    required_argument, nullptr, 'r'},
            {"copy", no_argument, &copy_flag, true},


    };
    while (true) {
        int option_index = 0;
        const auto opt =
                getopt_long(argc, argv, short_opts, long_opts, nullptr);
        if (opt == -1)
            break;
        switch (opt) {
            case 0:
                if (long_opts[option_index].flag != nullptr)
                    break;
                printf ("option %s", long_opts[option_index].name);
                if (optarg)
                    printf (" with arg %s", optarg);
                printf ("\n");
                break;

                break;
            case 'i':
                read_file_path = optarg;
                break;
            case 'o':
                write_file_path = optarg;
                break;
            case 'c':
                cols = std::stoi(optarg);
                break;
            case 'r':
                rows = std::stoi(optarg);
                break;
            default:
                std::cerr << "Parameter unsupported\n";
                std::terminate();
        }
    }

    if (write_file_path.empty()) {
        std::cerr << "no output file path given" << std::endl;
        std::terminate();
    }
    if (read_file_path.empty()) {
        std::cerr << "no input file path given" << std::endl;
        std::terminate();
    }
    if (cols <= 0 || rows <= 0) {
        std::cerr << "invalid matrix dimensions" << std::endl;
        std::terminate();
    }
    if (copy_flag) {
        std::cout << "copy flag is set" << std::endl;
    }
/*
    taco::Format dm({taco::Dense,taco::Dense});
    taco::Tensor<double> m({rows,cols},   dm);
    std::random_device rd;
    std::mt19937 gen(rd());
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            m.insert({i,j},i+j);
        }
    }
*/

    std::string filename = get_file_name_from_rows_and_cols(rows, cols, true);
    write_file_path += filename;
    read_file_path += filename;
    if (!copy_flag) {
        std::vector<std::vector<double>> matrix = generate_dense_matrix<double>(cols, rows, cols * rows, 1);
#if defined(BENCHMARK)
        auto t_begin = std::chrono::high_resolution_clock::now();
#endif
        write_dense_matrix_market_format(matrix, write_file_path);
#if defined(BENCHMARK)
        auto t_end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::duration<double>>(t_end - t_begin);
        std::cout << get_filesize((char *) write_file_path.c_str()) << std::endl;
        std::cout << "Elapsed time for write the matrix " << duration.count() << " seconds" << std::endl;
        auto f_size = get_filesize((char *) write_file_path.c_str());
        std::cout << "Matrix dimensions: " << rows << "x" << cols << std::endl;
        std::cout << "File size (Byte): " << f_size << std::endl;
        std::cout << "Bandwidth (Byte/s): " << f_size / duration.count() << std::endl;
#endif
    } else {
        std::cout << "copying the file" << std::endl;
#if defined(BENCHMARK)
        auto t_begin = std::chrono::high_resolution_clock::now();
#endif
        copy_file(read_file_path, write_file_path);
#if defined(BENCHMARK)
        auto t_end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::duration<double>>(t_end - t_begin);
        std::cout << get_filesize((char *) write_file_path.c_str()) << std::endl;
        std::cout << "Elapsed time for copy the matrix file " << duration.count() << " seconds" << std::endl;
        auto f_size = get_filesize((char *) write_file_path.c_str());
        std::cout << "Matrix dimensions: " << rows << "x" << cols << std::endl;
        std::cout << "File size (Byte): " << f_size << std::endl;
        std::cout << "Bandwidth (Byte/s): " << f_size / duration.count() << std::endl;
#endif
    }
    return 0;
}

