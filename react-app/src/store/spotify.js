// constants
const SPOTIFY_AUTH = "session/SPOTIFY_AUTH";


const spotifyAuth = () => ({
	type: SPOTIFY_AUTH,
	payload: Math.floor(Math.random()*100000),
});

export const spotifyLogin = () => async (dispatch) => {
	await fetch("/api/spotify/login")
		.then(response => {
			if (!response.ok) {
			throw new Error(response.statusText);
			}
			return response.json();
		}).catch(err=>{
		console.log(err);
		});
	dispatch(spotifyAuth());
}

const initialState = { spotifyAuthNum: null };

export default function reducer(state = initialState, action) {
	switch (action.type) {
		case SPOTIFY_AUTH:
			return { spotifyAuthNum: action.payload}
		default:
			return state;
	}
}
