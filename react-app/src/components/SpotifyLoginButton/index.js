import { useDispatch } from 'react-redux';
import './SpotifyLoginButton.css';
import { useEffect, useState } from 'react';

function SpotifyLoginButton() {
    const dispatch = useDispatch();
    const [accessToken, setAccessToken] = useState("");

    // useEffect to get accessToken if it exists and store in local storage
    useEffect(() => {
        if (!accessToken) {
            console.log("there isn't an access token...")
        }
    }, [])

    const handleClick = async(e) => {
        // to avoid CORS error by hitting Spotify login route w/ thunk, use direct backend address (works locally for now)
        window.location.href = 'http://localhost:5000/api/spotify/login';
    }

    return (
        <>
            <button onClick={handleClick}>
                Login to Spotify
            </button>
        </>
    );
}

export default SpotifyLoginButton;
