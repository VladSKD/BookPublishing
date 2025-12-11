#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <iomanip>
#include <memory> 
#include <windows.h> 
#include "json.hpp"

using json = nlohmann::json;
using namespace std;

const string DATA_FILE = "data.json";

// ==========================================
// БЕЗПЕЧНИЙ ПАРСИНГ: Захист від пробілів та некоректного формату
// ==========================================

double safe_stod(const char* str) {
    if (str == nullptr || *str == '\0') return 0.0;
    string s(str);
    size_t start = s.find_first_not_of(" \t\n\r");
    if (start == string::npos) return 0.0;
    
    try {
        return stod(s.substr(start));
    } catch (...) {
        return 0.0;
    }
}

int safe_stoi(const char* str) {
    if (str == nullptr || *str == '\0') return 0;
    string s(str);
    size_t start = s.find_first_not_of(" \t\n\r");
    if (start == string::npos) return 0;
    
    try {
        return stoi(s.substr(start));
    } catch (...) {
        return 0;
    }
}


// ==========================================
// 1. АБСТРАКЦІЇ ТА ІНТЕРФЕЙСИ
// ==========================================

class IAuthorStrategy {
public:
    virtual double calculateRoyalty(double baseSum, int run, double price, double royaltyPercent) const = 0;
    virtual ~IAuthorStrategy() = default;
};

class IPublishable {
protected:
    string title;
public:
    IPublishable(string t) : title(t) {}
    virtual double calculateProductionCost(int quantity) const = 0;
    virtual ~IPublishable() = default;
};

class IService {
public:
    virtual double calculateServiceCost(double volume, double rate) const = 0;
    virtual ~IService() = default;
};

// ==========================================
// 2. РЕАЛІЗАЦІЯ ІЄРАРХІЙ (Успадкування та Поліморфізм)
// ==========================================

class DomesticAuthor : public IAuthorStrategy {
public:
    double calculateRoyalty(double baseSum, int run, double price, double royaltyPercent) const override {
        return baseSum + (run * price * (royaltyPercent / 100.0));
    }
};

class IAuthorStrategy {
public:
    virtual double calculateRoyalty(double baseSum, int run, double price, double royaltyPercent) const = 0;
    virtual ~IAuthorStrategy() = default;
};

class ForeignAuthor : public IAuthorStrategy {
public:
    double calculateRoyalty(double baseSum, int run, double price, double royaltyPercent) const override {
        return (baseSum + (run * price * (royaltyPercent / 100.0))) * 1.1;
    }
};



class PhysicalBook : public IPublishable {
private:
    double paperCost;
    double printCost;
public:
    PhysicalBook(string t, double paper, double print) 
        : IPublishable(t), paperCost(paper), printCost(print) {}

    double calculateProductionCost(int quantity) const override {
        return quantity * (paperCost + printCost);
    }
};

class EBook : public IPublishable {
private:
    double conversionCost;
public:
    EBook(string t, double cost) 
        : IPublishable(t), conversionCost(cost) {}

    double calculateProductionCost(int quantity) const override {
        return quantity * conversionCost;
    }
};

class StandardWorker : public IService {
public:
    double calculateServiceCost(double volume, double rate) const override {
        return volume * rate;
    }
};

class TranslatorWorker : public IService {
public:
    double calculateServiceCost(double chars, double ratePer1000) const override {
        return (chars / 1000.0) * ratePer1000;
    }
};

// ==========================================
// 3. БІЗНЕС-ЛОГІКА (Композиція)
// ==========================================

class CalculationEngine {
public:
    double processAuthorContract(const IAuthorStrategy& author, double base, int run, double price, double royalty) {
        return author.calculateRoyalty(base, run, price, royalty);
    }

    double processProduction(const IPublishable& product, int run) {
        return product.calculateProductionCost(run);
    }

    double processService(const IService& service, double volume, double rate) {
        return service.calculateServiceCost(volume, rate);
    }
    
    double calculateBookstoreIncome(int count, double retailPrice, double discountPercent) {
        return count * (retailPrice * (1.0 - discountPercent / 100.0));
    }
    
    double calculateWarehouseRent(double area, double pricePerM2, int months) {
        return area * pricePerM2 * months;
    }
};

// ==========================================
// 4. КЛАС АНАЛІТИКИ (Checkout)
// ==========================================

class CheckoutSystem {
private:
    double calculateDelivery(double sum, double limit, double price) const {
        return (sum > limit) ? 0.0 : price;
    }

public:
    double calculateFinalPrice(double itemsTotal, bool isBirthday, double bonusesUsed, double freeLimit, double deliveryPrice) {
        double discounted = itemsTotal;
        
        if (isBirthday) {
            discounted *= 0.90; 
        }
        
        discounted -= bonusesUsed;
        if (discounted < 0) discounted = 0;
        
        double delCost = calculateDelivery(discounted, freeLimit, deliveryPrice);
        
        return discounted + delCost;
    }

    int calculateEarnedBonuses(double totalPaid) {
        return static_cast<int>(totalPaid / 20.0);
    }
};

// ==========================================
// 5. DATA MANAGER (Утиліта)
// ==========================================

class DataManager {
public:
    static void ensure_file_exists() {
        ifstream f(DATA_FILE);
        if (!f.good()) {
            json empty_db = {
                {"users", json::array()}, {"books", json::array()},
                {"contracts", json::array()}, {"orders", json::array()},
                {"news", json::array()}, {"postal_services", json::array()},
                {"projects", json::array()}, {"notifications", json::array()},
                {"wishlist", json::object()}, {"book_sets", json::array()}
            };
            save_json_to_file(empty_db);
        }
    }
    
    static json load_db() {
        ensure_file_exists();
        ifstream f(DATA_FILE);
        json data;
        try { f >> data; } catch (json::parse_error& e) { 
            cerr << "JSON Parse Error: " << e.what() << endl;
            return json::object(); 
        }
        return data;
    }
    
    static void save_json_to_file(const json& data) {
        ofstream f(DATA_FILE);
        f << data.dump(4, ' ', false); 
    }
};

// ==========================================
// MAIN (Контролер)
// ==========================================

int main(int argc, char* argv[]) {
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);

    if (argc < 2) return 0;

    string mode = argv[1];
    CalculationEngine engine;
    CheckoutSystem checkout;
    
    cout << fixed << setprecision(2);

    try {

        if (mode == "get_all") {
            cout << DataManager::load_db().dump(-1, ' ', false) << endl; 
        }
        else if (mode == "save_all_stdin") {
            string json_str;
            stringstream buffer;
            buffer << cin.rdbuf();
            json_str = buffer.str();
            if (!json_str.empty()) {
                DataManager::save_json_to_file(json::parse(json_str));
                cout << "OK" << endl;
            }
        }
        

        else if (mode == "con_author_ua") { 
            if (argc >= 6) {
                DomesticAuthor author; 
                cout << engine.processAuthorContract(author, safe_stod(argv[2]), safe_stoi(argv[3]), safe_stod(argv[4]), safe_stod(argv[5])) << endl;
            } else { cout << "0.00" << endl; } 
        }
        else if (mode == "con_author_foreign") {
            if (argc >= 6) {
                ForeignAuthor author;
                cout << engine.processAuthorContract(author, safe_stod(argv[2]), safe_stoi(argv[3]), safe_stod(argv[4]), safe_stod(argv[5])) << endl;
            } else { cout << "0.00" << endl; } 
        }

        else if (mode == "con_printer") { 
        if (argc >= 6) { 
            PhysicalBook book("Print Job", safe_stod(argv[4]), safe_stod(argv[5]));
            cout << engine.processProduction(book, safe_stoi(argv[2])) << endl; 
        } else { cout << "0.00" << endl; } 
    }
    else if (mode == "con_ebook") {
        if (argc >= 4) { 
            EBook book("Digital Job", safe_stod(argv[3])); 
            cout << engine.processProduction(book, safe_stoi(argv[2])) << endl; 
        } else { cout << "0.00" << endl; } 
    }
        

        else if (mode == "con_translator") {
            if (argc >= 4) {
                TranslatorWorker worker;
                cout << engine.processService(worker, safe_stod(argv[2]), safe_stod(argv[3])) << endl;
            } else { cout << "0.00" << endl; } 
        }


        else if (mode == "con_editor" || mode == "con_visual" || mode == "con_post" || mode == "con_audio") {
            if (argc >= 4) {
                StandardWorker worker;
                cout << engine.processService(worker, safe_stod(argv[2]), safe_stod(argv[3])) << endl;
            } else { cout << "0.00" << endl; } 
        }
        else if (mode == "con_reader") {

            if (argc >= 4) {
                double volume = safe_stod(argv[2]); 
                double rate = safe_stod(argv[3]);   
                double total = volume * rate;
                cout << total << endl;
            } else { 
                cout << "0.00" << endl; 
            } 
        }


        else if (mode == "con_bookstore") {

            if (argc >= 5) cout << engine.calculateBookstoreIncome(safe_stoi(argv[2]), safe_stod(argv[3]), safe_stod(argv[4])) << endl;
            else { cout << "0.00" << endl; } 
        }

        else if (mode == "con_warehouse") {

            if (argc >= 5) cout << engine.calculateWarehouseRent(safe_stod(argv[2]), safe_stod(argv[3]), safe_stoi(argv[4])) << endl;
            else { cout << "0.00" << endl; } 
        }


        else if (mode == "calc_final_checkout") {
            if (argc >= 7) {
                cout << checkout.calculateFinalPrice(safe_stod(argv[2]), safe_stoi(argv[3]), safe_stod(argv[4]), safe_stod(argv[5]), safe_stod(argv[6])) << endl;
            } else { cout << "0.00" << endl; } 
        }
        else if (mode == "calc_earned_bonuses") {
            if (argc >= 3) cout << checkout.calculateEarnedBonuses(safe_stod(argv[2])) << endl;
            else { cout << "0" << endl; } 
        }

        else {
            cout << "0.00" << endl;
        }

    } catch (const exception& e) {
        cout << "0.00" << endl; 
        return 1;
    }

    return 0;
}