from App import App

if __name__ == "__main__":
    app = App()
    app.scrape()
    app.set_database()
    app.get_data()
    app.print_class('FGA0008')
    app.close()