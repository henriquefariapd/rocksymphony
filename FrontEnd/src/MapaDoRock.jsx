import React, { useState, useEffect, useRef, useCallback } from "react";
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import "./MapaDoRock.css";

const MapaDoRock = () => {
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [progBandsByCountry, setProgBandsByCountry] = useState({});
  const [loadingArtists, setLoadingArtists] = useState(true);
  const [loadingMap, setLoadingMap] = useState(true);
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const geoLayerRef = useRef(null);
  const isLoadingRef = useRef(false);

  // Detectar se é dispositivo móvel
  const isMobile = window.innerWidth <= 768;

  // Buscar artistas da API
  const fetchArtists = async () => {
    try {
      setLoadingArtists(true);
      console.log("=== DEBUG FETCH ARTISTS MAPA ===");
      
      const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'https://rock-symphony-91f7e39d835d.herokuapp.com';
      
      const response = await fetch(`${apiUrl}/api/artists`);
      console.log("Response status:", response.status);
      console.log("API URL:", `${apiUrl}/api/artists`);
      
      if (response.ok) {
        const data = await response.json();
        console.log("Artists data:", data);
        const artists = data.artists || [];
        console.log("Number of artists:", artists.length);
        
        // Agrupar artistas por país
        const artistsByCountry = {};
        artists.forEach(artist => {
          const country = artist.origin_country;
          if (!artistsByCountry[country]) {
            artistsByCountry[country] = [];
          }
          artistsByCountry[country].push({
            name: artist.name,
            formed: artist.formed_year,
            description: artist.description || `${artist.genre || 'Progressive Rock'} - ${artist.members || 'Membros não informados'}`,
            genre: artist.genre,
            members: artist.members
          });
        });
        
        console.log("Artists by country:", artistsByCountry);
        setProgBandsByCountry(artistsByCountry);
      } else {
        console.error('Erro ao buscar artistas:', response.status);
        const responseText = await response.text();
        console.error('Response text:', responseText);
        // Manter dados hardcoded como fallback
        setProgBandsByCountry(getHardcodedBands());
      }
    } catch (error) {
      console.error('Erro ao buscar artistas:', error);
      console.error('Error details:', error.message);
      // Manter dados hardcoded como fallback
      setProgBandsByCountry(getHardcodedBands());
    } finally {
      setLoadingArtists(false);
      console.log("=== FINAL STATE ===");
      console.log("Loading finished, progBandsByCountry:", progBandsByCountry);
    }
  };

  // Dados hardcoded como fallback
  const getHardcodedBands = () => ({
    "United States": [
      { name: "Dream Theater", formed: 1985, description: "Metal progressivo com virtuosismo técnico" },
      { name: "Tool", formed: 1990, description: "Progressive metal com elementos alternativos" },
      { name: "Queensrÿche", formed: 1982, description: "Pioneiros do metal progressivo" },
      { name: "Fates Warning", formed: 1982, description: "Metal progressivo melódico" },
      { name: "Liquid Tension Experiment", formed: 1997, description: "Supergrupo instrumental" }
    ],
    "United Kingdom": [
      { name: "Pink Floyd", formed: 1965, description: "Lendas do rock progressivo atmosférico" },
      { name: "Yes", formed: 1968, description: "Virtuosismo e complexidade melódica" },
      { name: "Genesis", formed: 1967, description: "Evolução do prog teatral ao pop" },
      { name: "King Crimson", formed: 1968, description: "Experimentalismo e inovação constante" },
      { name: "Porcupine Tree", formed: 1987, description: "Progressive rock moderno" }
    ],
    "Canada": [
      { name: "Rush", formed: 1968, description: "Trio virtuoso com letras filosóficas" },
      { name: "Voivod", formed: 1982, description: "Progressive thrash metal" },
      { name: "Protest the Hero", formed: 1999, description: "Mathcore progressivo" }
    ],
    "Sweden": [
      { name: "Opeth", formed: 1990, description: "Death metal progressivo melódico" },
      { name: "Pain of Salvation", formed: 1991, description: "Progressive metal conceitual" },
      { name: "Katatonia", formed: 1991, description: "Progressive rock melancólico" }
    ],
    "Netherlands": [
      { name: "Focus", formed: 1969, description: "Prog rock com elementos de jazz" },
      { name: "Ayreon", formed: 1995, description: "Óperas rock progressivas" },
      { name: "The Gathering", formed: 1989, description: "Atmospheric progressive rock" }
    ],
    "Germany": [
      { name: "Helloween", formed: 1984, description: "Power metal progressivo" },
      { name: "Blind Guardian", formed: 1984, description: "Power metal sinfônico" },
      { name: "Rammstein", formed: 1994, description: "Industrial metal com elementos prog" }
    ],
    "Italy": [
      { name: "Banco del Mutuo Soccorso", formed: 1969, description: "Prog rock italiano clássico" },
      { name: "Premiata Forneria Marconi", formed: 1970, description: "RPI (Rock Progressivo Italiano)" },
      { name: "Goblin", formed: 1972, description: "Prog rock com trilhas sonoras" }
    ],
    "France": [
      { name: "Magma", formed: 1969, description: "Zeuhl - prog rock avant-garde" },
      { name: "Ange", formed: 1969, description: "Prog rock teatral francês" },
      { name: "Gojira", formed: 1996, description: "Progressive death metal" }
    ],
    "Japan": [
      { name: "Boris", formed: 1992, description: "Experimental heavy music" },
      { name: "Ruins", formed: 1985, description: "Math rock progressivo" },
      { name: "Acid Mothers Temple", formed: 1995, description: "Psychedelic prog" }
    ],
    "Australia": [
      { name: "Karnivool", formed: 1997, description: "Progressive rock alternativo" },
      { name: "Ne Obliviscaris", formed: 2003, description: "Progressive extreme metal" },
      { name: "Caligula's Horse", formed: 2011, description: "Progressive metal melódico" }
    ],
    "Norway": [
      { name: "Leprous", formed: 2001, description: "Progressive metal moderno" },
      { name: "Ihsahn", formed: 2006, description: "Progressive black metal" },
      { name: "Green Carnation", formed: 1990, description: "Progressive metal melódico" }
    ],
    "Finland": [
      { name: "Amorphis", formed: 1990, description: "Progressive death/folk metal" },
      { name: "Moonsorrow", formed: 1995, description: "Progressive folk metal épico" },
      { name: "Insomnium", formed: 1997, description: "Melodic death metal progressivo" }
    ],
    "Brazil": [
      { name: "Angra", formed: 1991, description: "Power metal progressivo brasileiro" },
      { name: "Sepultura", formed: 1984, description: "Thrash/groove metal com elementos prog" },
      { name: "Shaman", formed: 2000, description: "Progressive power metal" }
    ],
    "Argentina": [
      { name: "Serú Girán", formed: 1978, description: "Rock progressivo argentino" },
      { name: "Sui Generis", formed: 1969, description: "Rock progressivo folk" },
      { name: "Los Jaivas", formed: 1963, description: "Progressive rock andino" }
    ],
    "Israel": [
      { name: "Orphaned Land", formed: 1991, description: "Progressive oriental metal" },
      { name: "Scardust", formed: 2015, description: "Progressive metal sinfônico" }
    ]
  });

  useEffect(() => {
    fetchArtists();
  }, []);

  // Mapeamento de nomes de países do GeoJSON para nossas chaves
  const countryNameMapping = {
    "United States of America": "United States",
    "United States": "United States",
    "United Kingdom": "United Kingdom",
    "Canada": "Canada", 
    "Sweden": "Sweden",
    "Netherlands": "Netherlands",
    "Germany": "Germany",
    "Italy": "Italy",
    "France": "France",
    "Japan": "Japan",
    "Australia": "Australia",
    "Norway": "Norway",
    "Finland": "Finland",
    "Brazil": "Brazil",
    "Argentina": "Argentina",
    "Israel": "Israel",
    // Adicionar possíveis variações comuns em GeoJSON
    "USA": "United States",
    "US": "United States",
    "UK": "United Kingdom",
    "Brasil": "Brazil",
  };

  // Tradução dos nomes dos países
  const countryTranslations = {
    "United States": "Estados Unidos",
    "United Kingdom": "Reino Unido", 
    "Canada": "Canadá",
    "Sweden": "Suécia",
    "Netherlands": "Holanda",
    "Germany": "Alemanha",
    "Italy": "Itália",
    "France": "França",
    "Japan": "Japão",
    "Australia": "Austrália",
    "Norway": "Noruega",
    "Finland": "Finlândia",
    "Brazil": "Brasil",
    "Argentina": "Argentina",
    "Israel": "Israel"
  };

  const loadGeoData = useCallback(async (map) => {
    console.log('=== DEBUG LOAD GEO DATA ===');
    console.log('Map instance:', map);
    console.log('progBandsByCountry keys:', Object.keys(progBandsByCountry));
    console.log('isLoadingRef.current:', isLoadingRef.current);
    console.log('geoLayerRef.current:', geoLayerRef.current);
    
    // Verificação tripla de segurança
    if (isLoadingRef.current || geoLayerRef.current || !map || !map.getContainer()) {
      console.log('GeoJSON já carregado, em carregamento, ou mapa inválido - ignorando...');
      return;
    }

    // Marcar como carregando IMEDIATAMENTE
    isLoadingRef.current = true;

    try {
      console.log('Iniciando carregamento do GeoJSON...');
      
      // Verificar novamente antes do fetch (pode ter mudado durante o await)
      if (geoLayerRef.current) {
        console.log('Camada já existe, cancelando carregamento...');
        return;
      }
      
      // Usar uma API pública para dados geográficos dos países
      const response = await fetch('https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const geoData = await response.json();
      console.log('GeoJSON carregado:', geoData.features.length, 'países');

      // Verificar mais uma vez antes de criar a camada
      if (geoLayerRef.current || !map.getContainer()) {
        console.log('Camada já existe ou mapa inválido após fetch, cancelando...');
        return;
      }

      // Adicionar camada dos países
      const geoLayer = L.geoJSON(geoData, {
        style: (feature) => {
          const geoCountryName = feature.properties.name;
          const mappedCountryName = countryNameMapping[geoCountryName] || geoCountryName;
          const hasProgBands = progBandsByCountry.hasOwnProperty(mappedCountryName);
          
          return {
            fillColor: hasProgBands ? '#8B1538' : '#34495e',
            weight: 1,
            opacity: 1,
            color: '#ffffff',
            dashArray: '',
            fillOpacity: hasProgBands ? 0.7 : 0.3
          };
        },
        onEachFeature: (feature, layer) => {
          const geoCountryName = feature.properties.name;
          const mappedCountryName = countryNameMapping[geoCountryName] || geoCountryName;
          const hasProgBands = progBandsByCountry.hasOwnProperty(mappedCountryName);
          
          if (hasProgBands) {
            console.log(`País com dados: ${geoCountryName} -> ${mappedCountryName}`);
          }
          
          if (hasProgBands) {
            layer.setStyle({
              fillColor: '#8B1538',
              fillOpacity: 0.7
            });

            layer.on({
              mouseover: (e) => {
                const layer = e.target;
                layer.setStyle({
                  fillOpacity: 0.9,
                  weight: 3
                });
              },
              mouseout: (e) => {
                const layer = e.target;
                layer.setStyle({
                  fillOpacity: 0.7,
                  weight: 1
                });
              },
              click: (e) => {
                setSelectedCountry(mappedCountryName);
                // Zoom no país clicado
                map.fitBounds(e.target.getBounds());
              }
            });

            // Adicionar tooltip
            const translatedName = countryTranslations[mappedCountryName] || mappedCountryName;
            const bandCount = progBandsByCountry[mappedCountryName].length;
            layer.bindTooltip(`
              <div style="text-align: center; font-family: Arial, sans-serif;">
                <strong style="color: #8B1538;">${translatedName}</strong><br>
                <span style="color: #666;">${bandCount} bandas de prog rock</span>
              </div>
            `, {
              permanent: false,
              direction: 'top',
              offset: [0, -10]
            });
          } else {
            // Países sem dados
            layer.bindTooltip(`
              <div style="text-align: center; font-family: Arial, sans-serif;">
                <span style="color: #666;">${geoCountryName}</span><br>
                <small style="color: #999;">Sem dados de prog rock</small>
              </div>
            `, {
              permanent: false,
              direction: 'top',
              offset: [0, -10]
            });
          }
        }
      });

      // Adicionar ao mapa de forma segura com verificação final
      if (map && map.getContainer() && !geoLayerRef.current) {
        geoLayer.addTo(map);
        geoLayerRef.current = geoLayer;
        console.log('Camada GeoJSON adicionada com sucesso!');
        console.log('Mapa bounds:', map.getBounds());
      } else {
        console.log('Não foi possível adicionar camada - condições não atendidas');
      }

    } catch (error) {
      console.error('Erro ao carregar dados GeoJSON:', error);
    } finally {
      // Resetar flag de carregamento sempre
      isLoadingRef.current = false;
      console.log('=== FIM LOAD GEO DATA ===');
    }
  }, [progBandsByCountry, countryTranslations]);

  // Recarregar mapa quando os dados dos artistas mudarem
  useEffect(() => {
    console.log('=== DEBUG ARTIST DATA CHANGE ===');
    console.log('loadingArtists:', loadingArtists);
    console.log('mapInstanceRef.current:', mapInstanceRef.current);
    console.log('progBandsByCountry keys:', Object.keys(progBandsByCountry));
    console.log('progBandsByCountry length:', Object.keys(progBandsByCountry).length);
    
    if (!loadingArtists && mapInstanceRef.current && Object.keys(progBandsByCountry).length > 0) {
      console.log('Condições atendidas - recarregando dados do mapa');
      
      // Remover layer anterior se existir
      if (geoLayerRef.current) {
        console.log('Removendo layer anterior');
        mapInstanceRef.current.removeLayer(geoLayerRef.current);
        geoLayerRef.current = null;
        isLoadingRef.current = false;
      }
      // Recarregar dados geográficos
      loadGeoData(mapInstanceRef.current);
    } else {
      console.log('Condições não atendidas para recarregar dados');
    }
  }, [loadingArtists, progBandsByCountry, loadGeoData]);

  useEffect(() => {
    // Criar uma flag local para este useEffect específico
    let isCurrentEffectActive = true;
    let initializationAttempts = 0;
    const maxAttempts = 10; // Aumentar tentativas para mobile
    
    console.log('=== DEBUG MAP INITIALIZATION ===');
    
    const initializeMap = () => {
      initializationAttempts++;
      console.log(`Tentativa de inicialização ${initializationAttempts}/${maxAttempts}`);
      console.log('mapRef.current:', mapRef.current);
      console.log('mapInstanceRef.current:', mapInstanceRef.current);
      
      if (!isCurrentEffectActive) {
        console.log('Effect não está mais ativo, cancelando inicialização');
        return;
      }
      
      if (!mapRef.current) {
        console.log('mapRef.current não está disponível ainda');
        if (initializationAttempts < maxAttempts) {
          setTimeout(initializeMap, 300 * initializationAttempts); // Aumentar delay para mobile
        }
        return;
      }
      
      if (mapInstanceRef.current) {
        console.log('Mapa já foi inicializado');
        return;
      }
      
      try {
        console.log('Inicializando mapa...');
        
        // Verificar se o container está visível
        const container = mapRef.current;
        const rect = container.getBoundingClientRect();
        console.log('Container dimensions:', { width: rect.width, height: rect.height });
        
        if (rect.width === 0 || rect.height === 0) {
          console.log('Container ainda não tem dimensões, tentando novamente...');
          if (initializationAttempts < maxAttempts) {
            setTimeout(initializeMap, 400 * initializationAttempts); // Aumentar delay para mobile
          }
          return;
        }
        
        // Forçar dimensões mínimas no mobile
        const isMobile = window.innerWidth <= 768;
        if (isMobile && rect.height < 300) {
          container.style.height = '350px';
          console.log('Forçando altura mínima para mobile');
        }
        
        // Limpar qualquer conteúdo anterior do container
        container.innerHTML = '';
        
        // Configurações específicas para mobile
        const mapOptions = {
          center: [20, 0],
          zoom: isMobile ? 1 : 2, // Zoom menor no mobile
          minZoom: 1,
          maxZoom: isMobile ? 4 : 6, // Menos zoom no mobile
          worldCopyJump: true,
          maxBounds: [[-90, -180], [90, 180]],
          preferCanvas: true, // Melhor performance no mobile
          zoomControl: true,
          attributionControl: true,
          // Configurações específicas para touch
          tap: true,
          tapTolerance: 15,
          touchZoom: true,
          bounceAtZoomLimits: false,
          zoomSnap: 0.5,
          zoomDelta: 0.5
        };
        
        // Inicializar o mapa
        const map = L.map(container, mapOptions);

        console.log('Mapa criado:', map);

        // Múltiplos invalidateSize para garantir dimensões corretas
        const invalidateMapSize = () => {
          if (map && isCurrentEffectActive) {
            map.invalidateSize();
            console.log('InvalidateSize executado');
          }
        };

        // Forçar invalidateSize múltiplas vezes
        setTimeout(invalidateMapSize, 100);
        setTimeout(invalidateMapSize, 300);
        setTimeout(invalidateMapSize, 600);

        // Adicionar layer do mapa com múltiplos fallbacks
        const tileUrls = [
          'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
          'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png'
        ];
        
        let currentUrlIndex = 0;
        
        const createTileLayer = (urlIndex = 0) => {
          return L.tileLayer(tileUrls[urlIndex], {
            attribution: urlIndex === 0 ? '© OpenStreetMap contributors © CARTO' : '© OpenStreetMap contributors',
            subdomains: urlIndex === 0 ? 'abcd' : 'abc',
            maxZoom: 19,
            timeout: 10000 // Timeout de 10 segundos
          });
        };

        const tileLayer = createTileLayer(currentUrlIndex);

        // Adicionar listeners para debug e fallback
        tileLayer.on('loading', () => console.log('Tiles começaram a carregar'));
        tileLayer.on('load', () => console.log('Tiles carregaram'));
        tileLayer.on('tileerror', (e) => {
          console.log('Erro ao carregar tile:', e);
          
          // Tentar próximo URL em caso de erro
          if (currentUrlIndex < tileUrls.length - 1) {
            currentUrlIndex++;
            console.log(`Tentando URL de fallback ${currentUrlIndex}: ${tileUrls[currentUrlIndex]}`);
            
            map.removeLayer(tileLayer);
            const fallbackLayer = createTileLayer(currentUrlIndex);
            fallbackLayer.addTo(map);
          }
        });

        tileLayer.addTo(map);
        console.log('Tile layer adicionado');
        
        mapInstanceRef.current = map;
        console.log('Map instance ref definido');

        // Aguardar o mapa e tiles carregarem
        map.whenReady(() => {
          console.log('Mapa pronto!');
          
          // Forçar invalidateSize após estar pronto
          setTimeout(invalidateMapSize, 200);
          setTimeout(invalidateMapSize, 500);
          
          // Marcar mapa como carregado
          setTimeout(() => {
            setLoadingMap(false);
          }, 1000);
          
          // Verificar se este useEffect ainda está ativo
          if (isCurrentEffectActive && !geoLayerRef.current) {
            setTimeout(() => {
              console.log('Iniciando carregamento dos dados geográficos...');
              if (isCurrentEffectActive && !geoLayerRef.current) {
                loadGeoData(map);
              }
            }, isMobile ? 1000 : 500); // Mais delay no mobile
          }
        });
        
        // Adicionar um listener para resize da janela e orientação
        const handleResize = () => {
          if (map && isCurrentEffectActive) {
            setTimeout(invalidateMapSize, 100);
          }
        };
        
        const handleOrientationChange = () => {
          if (map && isCurrentEffectActive) {
            setTimeout(() => {
              invalidateMapSize();
              // Re-centralizar no mobile após rotação
              if (window.innerWidth <= 768) {
                map.setView([20, 0], window.innerWidth <= 480 ? 1 : 2);
              }
              // Força uma atualização completa do mapa
              setTimeout(() => {
                invalidateMapSize();
                console.log('Mapa atualizado após mudança de orientação');
              }, 500);
            }, 500);
          }
        };
        
        window.addEventListener('resize', handleResize);
        window.addEventListener('orientationchange', handleOrientationChange);
        
        // Salvar as funções de cleanup
        map._resizeHandler = handleResize;
        map._orientationHandler = handleOrientationChange;
        
      } catch (error) {
        console.error('Erro ao inicializar mapa:', error);
        
        // Tentar novamente se houver erro
        if (initializationAttempts < maxAttempts) {
          console.log('Tentando novamente em 2 segundos...');
          setTimeout(initializeMap, 2000);
        }
      }
    };

    // Aguardar mais tempo no mobile para garantir que o DOM esteja pronto
    const isMobile = window.innerWidth <= 768;
    const initialDelay = setTimeout(() => {
      if (isCurrentEffectActive) {
        initializeMap();
      }
    }, isMobile ? 300 : 100);

    return () => {
      // Marcar que este useEffect não está mais ativo
      isCurrentEffectActive = false;
      console.log('Cleanup do mapa');
      
      // Limpar timeout se ainda estiver pendente
      clearTimeout(initialDelay);
      
      if (mapInstanceRef.current) {
        try {
          // Remover listeners se existirem
          if (mapInstanceRef.current._resizeHandler) {
            window.removeEventListener('resize', mapInstanceRef.current._resizeHandler);
          }
          if (mapInstanceRef.current._orientationHandler) {
            window.removeEventListener('orientationchange', mapInstanceRef.current._orientationHandler);
          }
          
          // Remover camada GeoJSON se existir
          if (geoLayerRef.current) {
            mapInstanceRef.current.removeLayer(geoLayerRef.current);
            geoLayerRef.current = null;
          }
          
          mapInstanceRef.current.remove();
        } catch (error) {
          console.log('Erro ao remover mapa:', error);
        }
        mapInstanceRef.current = null;
        isLoadingRef.current = false;
      }
    };
  }, []);

  const resetMapView = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([20, 0], 2);
      setSelectedCountry(null);
    }
  };

  const getDisplayName = (countryName) => {
    return countryTranslations[countryName] || countryName;
  };

  return (
    <div className="mapa-do-rock-container">
      <h1>Mapa do Rock Progressivo</h1>
      {(loadingArtists || loadingMap) && (
        <div className="loading-indicator">
          <p>
            {loadingArtists ? 'Carregando artistas da base de dados...' : 
             loadingMap ? (isMobile ? 'Carregando mapa (pode levar alguns segundos no mobile)...' : 'Carregando mapa...') :
             'Carregando...'}
          </p>
        </div>
      )}
      <div className="mapa-content">
        {!loadingArtists && (
        <>
        {/* Sidebar esquerda com bandas */}
        <div className="bands-sidebar">
          {selectedCountry ? (
            <div className="country-bands">
              <div className="country-header">
                <h2>{getDisplayName(selectedCountry)}</h2>
                <button className="reset-btn" onClick={resetMapView}>
                  🌍 Ver Mapa Completo
                </button>
              </div>
              <p className="country-subtitle">Maiores bandas de Prog Rock</p>
              <div className="bands-list">
                {progBandsByCountry[selectedCountry].map((band, index) => (
                  <div key={index} className="band-card">
                    <h3>{band.name}</h3>
                    <p className="band-year">Formada em {band.formed}</p>
                    <p className="band-description">{band.description}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="no-selection">
              <h2>🎸 Explore o Mundo do Prog</h2>
              <p>Clique em um país destacado no mapa para descobrir suas maiores bandas de rock progressivo!</p>
              <div className="instruction">
                <span className="click-icon">👆</span>
                <span>Países em <strong style={{color: '#8B1538'}}>vermelho</strong> possuem dados de bandas prog. {isMobile ? 'Toque' : 'Use o mouse'} para navegar pelo mapa 360°!</span>
              </div>
              <div className="map-legend">
                <h4>Legenda:</h4>
                <div className="legend-item">
                  <span className="legend-color prog"></span>
                  <span>Países com bandas prog rock</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color no-data"></span>
                  <span>Outros países</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Mapa mundial real */}
        <div className="world-map-real">
          {loadingMap && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: '#8B1538',
              fontSize: '18px',
              fontWeight: 'bold'
            }}>
              {isMobile ? 'Carregando mapa para mobile...' : 'Carregando mapa...'}
            </div>
          )}
          <div 
            ref={mapRef} 
            className="leaflet-map"
            style={{ opacity: loadingMap ? 0 : 1, transition: 'opacity 0.5s ease' }}
          />
        </div>
        </>
        )}
      </div>
    </div>
  );
};

export default MapaDoRock;
