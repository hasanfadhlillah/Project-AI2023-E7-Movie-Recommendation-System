import pickle
import streamlit as st

# Cache sederhana untuk menyimpan rekomendasi
cache = {}

# Fungsi untuk memberikan rekomendasi film
def recommend(selected_movies, recommendation_data):
    if selected_movies in cache:
        # Mengembalikan hasil dari cache jika tersedia
        return cache[selected_movies]

    movies = recommendation_data['data']
    similarity = recommendation_data['similarity']

    # Mendapatkan indeks film yang dipilih
    selected_indices = [movies[movies['Series_Title'] == movie].index[0] for movie in selected_movies]

    # Menghitung total jarak kesamaan untuk setiap film
    distances_sum = [0] * len(movies)
    for index in selected_indices:
        distances = similarity[index]
        distances_sum = [distances_sum[i] + distances[i] for i in range(len(distances_sum))]

    # Menetapkan nilai negatif tak terhingga untuk film yang sudah dipilih
    for index in selected_indices:
        distances_sum[index] = float('-inf')

    # Mengurutkan film berdasarkan total jarak kesamaan
    sorted_movies = sorted(list(enumerate(distances_sum)), reverse=True, key=lambda x: x[1])

    recommended_movie_details = []
    # Mengambil detail 10 film teratas yang direkomendasikan
    for i in sorted_movies[:10]:
        movie_index = i[0]
        movie_data = movies.iloc[movie_index]
        recommended_movie_details.append({
            'Title': movie_data['Series_Title'],
            'Released Year': movie_data['Released_Year'],
            'Certificate': movie_data['Certificate'],
            'Movie Runtime': movie_data['Runtime'],
            'Genre': movie_data['Genre'],
            'IMDB Rating': movie_data['IMDB_Rating'],
            'Director': movie_data['Director'],
            'Overview': movie_data['Overview'],
            'Alternatif Poster': movie_data['Poster_Link']
        })

    # Menyimpan hasil ke cache
    cache[selected_movies] = recommended_movie_details

    return recommended_movie_details

# Membaca data rekomendasi dari file pickle
with open('artifacts/recommendation_data.pkl', 'rb') as f:
    recommendation_data = pickle.load(f)

if __name__ == '__main__':
    st.header('CINEFY: MOVIE RECOMMENDATION SYSTEM')

    # Membuat daftar film untuk dipilih
    movie_list = recommendation_data['data']['Series_Title'].values

    # Menerima input dari pengguna menggunakan multiselect
    selected_movies = st.multiselect(
        "Ketik atau pilih film dari dropdown",
        movie_list,
        default=[movie_list[0]]
    )

    button_clicked = st.button('Tampilkan Rekomndasi Film')

    if len(selected_movies) > 0 and button_clicked:
        # Mengubah film_terpilih menjadi tuple
        selected_movies_tuple = tuple(selected_movies)
        recommended_movie_details = recommend(selected_movies_tuple, recommendation_data)

        # Menampilkan detail 10 film teratas yang direkomendasikan
        st.subheader('Top 10 Film yang Direkomendasikan:')
        for i, movie_details in enumerate(recommended_movie_details, start=1):
            st.write(f"{i}. **{movie_details['Title']}**")
            st.image(movie_details['Alternatif Poster'], caption=movie_details['Title'], width=200)
            st.write(f"Released Year: {movie_details['Released Year']}")
            st.write(f"Certificate: {movie_details['Certificate']}")
            st.write(f"Movie Runtime: {movie_details['Movie Runtime']} minutes")
            st.write(f"Genre: {movie_details['Genre']}")
            st.write(f"IMDB Rating: {movie_details['IMDB Rating']}")
            st.write(f"Director: {movie_details['Director']}")
            st.write(f"Movie Overview: {movie_details['Overview']}")
            st.markdown("---")

        # Membuat opsi untuk filter berdasarkan genre dan tahun rilis
        unique_genres = list(set([movie_details['Genre'] for movie_details in recommended_movie_details]))
        unique_years = list(set([movie_details['Released Year'] for movie_details in recommended_movie_details]))

        selected_genre = st.selectbox("Pilih Genre untuk Difilter:", ["All"] + unique_genres)
        selected_year = st.selectbox("Pilih Tahun Rilis untuk Difilter:", ["All"] + unique_years)

        # Menyediakan tombol untuk menerapkan dan mereset filter
        apply_filters = st.button('Terapkan Filter dari Hasil Rekomendasi Film')
        reset_filters = st.checkbox('Reset Filter')

        if apply_filters:
            # Melakukan filter berdasarkan genre dan tahun rilis
            filtered_movies = [movie_details for movie_details in recommended_movie_details
                               if (selected_genre == "All" or movie_details['Genre'] == selected_genre)
                               and (selected_year == "All" or movie_details['Released Year'] == selected_year)]

            if not filtered_movies:
                st.warning(f"Tidak ada film yang ditemukan untuk Genre: {selected_genre}, Tahun Rilis: {selected_year}")
            else:
                # Menampilkan film yang terfilter
                st.subheader(f"Film Terfilter untuk Genre: {selected_genre}, Tahun Rilis: {selected_year}")
                for i, movie_details in enumerate(filtered_movies, start=1):
                    st.write(f"{i}. **{movie_details['Title']}**")
                    st.image(movie_details['Alternatif Poster'], caption=movie_details['Title'], width=200)
                    st.write(f"Released Year: {movie_details['Released Year']}")
                    st.write(f"Certificate: {movie_details['Certificate']}")
                    st.write(f"Movie Runtime: {movie_details['Movie Runtime']} minutes")
                    st.write(f"Genre: {movie_details['Genre']}")
                    st.write(f"IMDB Rating: {movie_details['IMDB Rating']}")
                    st.write(f"Director: {movie_details['Director']}")
                    st.write(f"Movie Overview: {movie_details['Overview']}")
                    st.markdown("---")

        if reset_filters:
            selected_genre = "All"
            selected_year = "All"

    else:
        st.warning("Silakan pilih setidaknya satu film sebelum mengeklik 'Tampilkan Rekomendasi Film Anda'.")