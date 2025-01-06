

def calculate_score(price, mileage, year, max_price, max_mileage, min_year=None, max_year=None,
                    raw_weight_price=1, raw_weight_mileage=1, raw_weight_year=1):
    """
    Calculate the weighted score for a car using user-defined weights.
    If all weights are zero, return a neutral score (50).
    """
    total_weight = raw_weight_price + raw_weight_mileage + raw_weight_year

    if total_weight == 0:
        # All weights are zero, return a neutral score
        return 50

    # Normalize weights
    weight_price = raw_weight_price / total_weight
    weight_mileage = raw_weight_mileage / total_weight
    weight_year = raw_weight_year / total_weight

    # Normalize inputs
    normalized_price = price / max_price if max_price > 0 else 0
    normalized_mileage = mileage / max_mileage if max_mileage > 0 else 0
    normalized_year = 0
    if min_year is not None and max_year is not None and max_year > min_year:
        normalized_year = (year - min_year) / (max_year - min_year)

    # Calculate weighted score
    score = (
        weight_price * (1 - normalized_price) +
        weight_mileage * (1 - normalized_mileage) +
        weight_year * normalized_year
    )

    # Scale score to 0-100
    scaled_score = score * 100
    rounded_score = round(scaled_score, 3)
    return rounded_score


def fetch_car_data_with_scores(mode, items=None, raw_weight_price=0, raw_weight_mileage=0, raw_weight_year=0,
                               scraping_car=None):
    import sqlite3
    print(f'{mode} is the mode')

    # Connect to the database
    con = sqlite3.connect("Scraper.db")
    con.execute('PRAGMA journal_mode=WAL;')
    cur = con.cursor()
    results = None

    try:
        # Base query
        base_query = """
            SELECT Items.name, Items.Link, CarDetails.price, CarDetails.miles, CarDetails.year, Items.date_added
            FROM Items
            JOIN CarDetails ON Items.item_id = CarDetails.item_id
        """

        # Add filters based on mode
        if mode == 'search':
            car_brand_pattern = f"%{items[0]}%" if items[0] else "%"
            car_model_pattern = f"%{items[1]}%" if items[1] else "%"
            base_query += " WHERE CarDetails.make LIKE ? AND CarDetails.model LIKE ?"
            params = [car_brand_pattern, car_model_pattern]

            # Add year filtering if provided
            year_range = items[2] if items[2] else None
            if year_range:
                if len(year_range) == 2:  # Year range
                    base_query += " AND CarDetails.year BETWEEN ? AND ?"
                    params.extend(year_range)
                elif len(year_range) == 1:  # Single year
                    base_query += " AND CarDetails.year = ?"
                    params.append(year_range[0])

            # Add mileage filtering if provided
            mileage = items[3]
            if mileage:
                base_query += " AND CarDetails.miles < ?"
                params.append(mileage)

            cur.execute(base_query, params)

        elif mode == 'scrape':
            scraping_car_pattern = f"%{scraping_car}%"
            base_query += " WHERE Items.name LIKE ?"
            cur.execute(base_query, (scraping_car_pattern,))

        all_results = cur.fetchall()

        # For scrape mode, find the most recent added_date
        if mode == 'scrape':
            most_recent_date_query = """
                SELECT MAX(date_added)
                FROM Items
            """
            cur.execute(most_recent_date_query)
            most_recent_date = cur.fetchone()[0]

            # Filter items added on the most recent date
            recent_items = [row for row in all_results if row[-1] == most_recent_date]
        else:
            recent_items = all_results

        # Validate and extract data for scoring
        prices, mileages, years = [], [], []
        for row in all_results:
            try:
                price = float(row[2])
                mileage = float(row[3])
                year = row[4] if isinstance(row[4], int) else (
                    int(row[4]) if row[4] and str(row[4]).isdigit() else None)

                prices.append(price)
                mileages.append(mileage)
                if year:
                    years.append(year)
            except (ValueError, TypeError) as e:
                print(f"Skipping invalid data row: {row} ({e})")

        # Handle empty data cases
        if not prices or not mileages:
            print("No valid price or mileage data available.")
            return []

        # Normalization values
        max_price = max(prices)
        max_mileage = max(mileages)
        max_year = max(years) if years else None
        min_year = min(years) if years else None

        # Calculate scores for all items
        all_cars_with_scores = [
            {
                "name": row[0],
                "link": row[1],
                "price": float(row[2]),
                "miles": float(row[3]),
                "year": row[4] if isinstance(row[4], int) else (
                    int(row[4]) if row[4] and str(row[4]).isdigit() else None),
                "score": calculate_score(
                    float(row[2]), float(row[3]),
                    row[4] if isinstance(row[4], int) else (int(row[4]) if row[4] and str(row[4]).isdigit() else None),
                    max_price, max_mileage, min_year, max_year,
                    raw_weight_price, raw_weight_mileage, raw_weight_year
                )
            }
            for row in all_results
            if row[2] and row[3] and (row[4] is None or isinstance(row[4], int) or str(row[4]).isdigit())
        ]

        # Filter only recent items for scrape mode
        if mode == 'scrape':
            cars_with_scores = [
                car for car in all_cars_with_scores
                if any(car["link"] == recent_row[1] for recent_row in recent_items)
            ]
        else:
            cars_with_scores = all_cars_with_scores

        # Sort cars by score
        cars_with_scores = [car for car in cars_with_scores if car['miles'] >= 1000]
        sorted_cars = sorted(cars_with_scores, key=lambda x: x["score"], reverse=True)

        return sorted_cars

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        # Ensure the database connection is closed
        con.close()


if __name__ == '__main__':
    car_info_for_search = ['', '', [2000, 2010], '50000']
    results = fetch_car_data_with_scores(car_info_for_search)
    for i in results:
        print(i)

